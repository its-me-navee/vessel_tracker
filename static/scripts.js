let currentPage = 1;
const itemsPerPage = 10;
let currentVesselId = null;

// Bind click event to vessel names
$(document).ready(function() {
    $('.vessel-name').on('click', function(e) {
        e.preventDefault();
        currentPage = 1;
        currentVesselId = $(this).data('vessel-id');
        fetchVesselDetails(currentVesselId);
    });
});

function fetchVesselDetails(vesselId) {
    $.ajax({
        url: '/vessel/' + vesselId,
        method: 'GET',
        success: function(data) {
            displayVesselContents(data, currentPage);
        },
        error: function() {
            alert('Error fetching vessel details.');
        }
    });
}

function displayVesselContents(contents, page) {
    var contentsList = $('#contents-list');
    contentsList.empty();
    const startIndex = (page - 1) * itemsPerPage;
    const endIndex = Math.min(startIndex + itemsPerPage, contents.length);

    for (let i = startIndex; i < endIndex; i++) {
        contentsList.append('<tr><td class="table__cell">' + contents[i]['Item Name'] + '</td><td class="table__cell">' + contents[i]['Quantity'] + '</td></tr>');
    }

    $('#current-page').text(page);
    $('#prev-page').prop('disabled', page === 1);
    $('#next-page').prop('disabled', endIndex >= contents.length);

    $('#vessel-contents').show();
}

function hideVesselContents() {
    $('#vessel-contents').hide();
}

function nextPage() {
    currentPage++;
    fetchVesselDetails(currentVesselId);
}

function prevPage() {
    currentPage--;
    fetchVesselDetails(currentVesselId);
}
