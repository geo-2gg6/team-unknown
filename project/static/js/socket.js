document.addEventListener('DOMContentLoaded', function() {
    var socket = io();
    var feed = document.getElementById('live-feed');
    if (!feed) return;
    socket.on('new_event', function(data) {
        // Parse status from details if present
        let status = 'unknown';
        if (data.details && data.details.toLowerCase().includes('risky')) status = 'risky';
        else if (data.details && data.details.toLowerCase().includes('warning')) status = 'warning';
        else if (data.details && data.details.toLowerCase().includes('secure')) status = 'secure';
        let statusClass = 'status-' + status;
        let statusTextClass = 'status-' + status + '-text';
        let statusBgClass = 'status-' + status + '-bg-light';
        var item = document.createElement('div');
        item.className = `bg-white/10 p-4 rounded-xl flex items-center mb-2`;
        item.innerHTML = `
            <div class="rounded-full ${statusBgClass} flex items-center justify-center h-12 w-12 text-xl">
                <span class="font-bold ${statusTextClass}">${data.event_type.charAt(0).toUpperCase()}</span>
            </div>
            <div class="flex-grow ml-4">
                <p class="font-semibold capitalize text-lg">${data.event_type}</p>
                <p class="text-sm text-white/60">${data.timestamp}</p>
            </div>
            <div class="text-xs font-bold uppercase px-3 py-1 rounded-full text-white ${statusClass}">${status}</div>
        <div class="w-full text-white/80 mt-2">${data.details}</div>
        `;
        feed.prepend(item);
    });
});
