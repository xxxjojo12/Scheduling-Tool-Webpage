// /exam/flask_app/static/js/dashboard.js

console.log("dashboard.js loaded");

const socket = io();

socket.on("connect", () => {
    console.log("Socket connected!");

    // Join all event rooms based on data-event-id elements on the page
    const eventElements = document.querySelectorAll("[data-event-id]");
    eventElements.forEach(el => {
        const eventId = el.getAttribute("data-event-id");
        socket.emit("join", { event_id: eventId });
        console.log("Joined room for event:", eventId);
    });
		
});

// Listen for event_deleted broadcast from the server
	socket.on("event_deleted", (data) => {
    console.log("Event deleted:", data);
    const { event_id } = data;
    const item = document.querySelector(`[data-event-id="${event_id}"]`);
    if (item) {
        item.remove();
        console.log(`Removed event ${event_id} from DOM`);
    } else {
        console.warn(`Could not find event ${event_id} in DOM`);
    }
});


// Listen for real-time new event creation
socket.on("event_created", (event) => {
    console.log("New event received:", event);

    const list = document.getElementById("invited-events");
    if (!list) return;

    // Check if an event already exists
    const exists = document.querySelector(`[data-event-id="${event.event_id}"]`);
    if (exists) return;

    // Create li element
    const li = document.createElement("li");
    li.setAttribute("data-event-id", event.event_id);

    const title = document.createElement("strong");
    title.textContent = event.title;

    const br1 = document.createElement("br");

    const dates = document.createElement("span");
    dates.textContent = `Dates: ${event.start_date} to ${event.end_date}`;

    const br2 = document.createElement("br");

    const link = document.createElement("a");
    link.href = `/event/${event.event_id}`;
    link.textContent = "View Event";

    li.appendChild(title);
    li.appendChild(br1);
    li.appendChild(dates);
    li.appendChild(br2);
    li.appendChild(link);

    list.appendChild(li);
});
