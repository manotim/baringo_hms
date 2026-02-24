// Initialize DataTables
$(document).ready(function() {
    if ($('.datatable').length) {
        $('.datatable').DataTable({
            pageLength: 25,
            language: {
                search: "Search records:",
                lengthMenu: "Show _MENU_ entries",
                info: "Showing _START_ to _END_ of _TOTAL_ records",
                paginate: {
                    first: "First",
                    last: "Last",
                    next: "Next",
                    previous: "Previous"
                }
            }
        });
    }
});

// Auto-hide alerts after 5 seconds
setTimeout(function() {
    $('.alert').fadeOut('slow');
}, 5000);

// Confirm delete actions
function confirmDelete(event, message) {
    if (!confirm(message || 'Are you sure you want to delete this record?')) {
        event.preventDefault();
    }
}

// Print function
function printRecord(recordId) {
    window.open('/print/' + recordId + '/', '_blank');
}

// Patient search
function searchPatient() {
    let searchTerm = $('#patientSearch').val();
    if (searchTerm.length > 2) {
        $.ajax({
            url: '/api/search-patients/',
            data: {term: searchTerm},
            success: function(data) {
                // Display results
                console.log(data);
            }
        });
    }
}