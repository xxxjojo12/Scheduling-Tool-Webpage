// /exam/flask_app/static/js/grid.js

const socket = io();

document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('grid')
    const modeSelect = document.getElementById('mode')
    const startDate = new Date(grid.dataset.startDate)
    const endDate = new Date(grid.dataset.endDate)
    const startTime = parseInt(grid.dataset.startTime)
    const endTime = parseInt(grid.dataset.endTime)

    const eventId = window.location.pathname.split('/').pop()
    socket.emit("join_event", eventId)

    const dateList = [];
    for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
        dateList.push(new Date(d));
    }

    const timeSlots = [];
    for (let hour = startTime; hour < endTime; hour++) {
        timeSlots.push(`${hour.toString().padStart(2, '0')}:00`)
        timeSlots.push(`${hour.toString().padStart(2, '0')}:30`)
    }

    grid.classList.add('grid')
    grid.style.gridTemplateColumns = `100px ${dateList.map(() => '80px').join(' ')}`

    grid.innerHTML += '<div class="grid-cell header">Time</div>'
    dateList.forEach(d => {
        grid.innerHTML += `<div class="grid-cell header">${d.getMonth()+1}/${d.getDate()}</div>`
    })

    timeSlots.forEach(t => {
        grid.innerHTML += `<div class="grid-cell header">${t}</div>`
        dateList.forEach(d => {
            const id = `${d.toISOString().slice(0,10)}_${t}`
            grid.innerHTML += `<div class="grid-cell" id="${id}" data-date="${d.toISOString().slice(0,10)}" data-time="${t}"></div>`
        })
    })

    let isDragging = false
    let currentMode = modeSelect.value

    modeSelect.addEventListener('change', e => {
        currentMode = e.target.value
        console.log("[mode change]", currentMode)
    })

    grid.addEventListener('mousedown', e => {
        if (e.target.classList.contains('grid-cell') && !e.target.classList.contains('header')) {
            isDragging = true
            console.log("mousedown on", e.target.dataset.date, e.target.dataset.time)
            applyMode(e.target)
        }
    })

    grid.addEventListener('mouseover', e => {
        if (isDragging && e.target.classList.contains('grid-cell') && !e.target.classList.contains('header')) {
            console.log("mouseover on", e.target.dataset.date, e.target.dataset.time)
            applyMode(e.target)
        }
    })

    document.addEventListener('mouseup', () => {
        isDragging = false
    })

    function applyMode(cell) {
        const day = cell.dataset.date
        const time = cell.dataset.time

        console.log("applyMode:", day, time, currentMode)

        cell.classList.remove('available', 'maybe', 'unavailable')
        cell.classList.add(currentMode)

        const payload = {
            event_id: eventId,
            day: day,
            time: time,
            status: currentMode
        }

        fetch('/api/availability/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                updateHeatmap()
                socket.emit("availability_update", payload)
            } else {
                console.error('Failed to save availability')
            }
        })
        .catch(err => console.error(err))
    }

    function renderSavedAvailability(data) {
        data.forEach(item => {
            const id = `${item.day}_${item.time}`
            const cell = document.getElementById(id)
            if (cell) {
                cell.classList.add(item.status.toLowerCase())
            }
        })
    }

    function updateHeatmap() {
        fetch(`/api/availability/all/${eventId}`)
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    const heatmap = data.data
                    Object.keys(heatmap).forEach(id => {
                        const cell = document.getElementById(id)
                        if (!cell) return

                        const { available, maybe, unavailable } = heatmap[id]
                        cell.style.opacity = '1.0'

                        if (available > 0) {
                            const level = Math.min(available, 3)
                            cell.style.backgroundColor = `rgba(0, 128, 0, ${0.3 + 0.2 * level})` // green
                        } else if (maybe > 0) {
                            cell.style.backgroundColor = '#ffe680' // yellow
                        } else if (unavailable > 0) {
                            cell.style.backgroundColor = '#e0e0e0' // light gray
                        } else {
                            cell.style.backgroundColor = ''
                        }
                    })
                }
            })
            .catch(err => console.error(err))
    }

    function updateBestTime() {
        fetch(`/api/best_time/${eventId}`)
            .then(res => res.json())
            .then(data => {
                const bestTimeEl = document.getElementById("best-time")
                if (data.success) {
                    bestTimeEl.textContent = `Best Time to Meet: ${data.day} at ${data.time}`
                } else {
                    bestTimeEl.textContent = `Best Time to Meet: ${data.message}`
                }
            })
            .catch(err => console.error("Error fetching best time:", err))
    }

    // Receive real-time updates
    socket.on("availability_update", (payload) => {
		console.log("[WebSocket] availability_update received", payload)
        updateHeatmap()
    })

    socket.on("best_time_update", () => {
        console.log("[WebSocket] best_time_update received")
        updateBestTime()
    })
	
	socket.on("event_deleted", (data) => {
    alert("This event has been deleted. You will be redirected to the dashboard.");
    window.location.href = "/dashboard";
});

    // Initial rendering
    fetch(`/api/availability/self/${eventId}`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                renderSavedAvailability(data.data)
                updateHeatmap()
                updateBestTime()
            }
        })
        .catch(err => console.error(err))
})
