function printDiv(divName, title){

    var header = document.getElementById('title-div');
    if (title) {
        header.innerHTML = `<h1>${title}</h1>`
    }
	var printContents = document.getElementById(divName).innerHTML;
	var originalContents = document.body.innerHTML;
	document.body.innerHTML = printContents;
	window.print();
	document.body.innerHTML = originalContents;

	var header = document.getElementById('title-div');
	header.innerHTML = ''
}

function deleteNotification(notificationId) {
	// returns user's notifications
	$.ajax({
		data: {  },
		type: "GET",
		url: `/delete-notification/${notificationId}`
	}).done(data=>{
		
	})
}

function getNotifications(){
	// returns user's notifications
	$.ajax({
		data: {  },
		type: "GET",
		url: "/notifications"
	}).done(data=>{
		
	})
}


function hodApprovePlan(planId, approvalBox, statusBox, row) {
	$(`#${statusBox}`).html(
		`<div class="spinner-border text-info " role="status"><span class="sr-only">Loading...</span></div>`
	)
	$.ajax({
		url: `/hod-approve-plan/${planId}`,
		method: 'GET',
		data: {  },
		success: function (data) {
			if (data) {
				plan = data.data.fields
				if (plan.hod_approved){
					$(`#${approvalBox}`).html(
						`<button onclick="hodApprovePlan('${planId}', 'approvalBox${planId}', 'statusBox${planId}', 'row${planId}')" class="btn btn-sm btn-block btn-danger" id="approveCheck{{plan.id}}">Disapprove</button>`
					)
					$(`#${statusBox}`).html(
						`APPROVED (HOD)`
					)
					$(`#${row}`).attr("class", "table-primary")
				}else{
					$(`#${approvalBox}`).html(
						`<button onclick="hodApprovePlan('${planId}', 'approvalBox${planId}', 'statusBox${planId}', 'row${planId}')" class="btn btn-sm btn-block btn-success" id="approveCheck{{plan.id}}">Approve</button>`
					)
					$(`#${statusBox}`).html(
						`PREPARED`
					)
					$(`#${row}`).attr("class", "")
				}
			}
		}
	});
}


function pduApprovePlan(planId, approvalBox, statusBox, row) {
	$(`#${statusBox}`).html(
		`<div class="spinner-border text-info " role="status"><span class="sr-only">Loading...</span></div>`
	)
	$.ajax({
		url: `/pdu-approve-plan/${planId}`,
		method: 'GET',
		data: {  },
		success: function (data) {
			if (data) {
				console.log(data)
				plan = data.data.fields
				if (plan.pdu_approved){
					$(`#${approvalBox}`).html(
						`<button onclick="pduApprovePlan('${planId}', 'approvalBox${planId}', 'statusBox${planId}', 'row${planId}')" class="btn btn-sm btn-block btn-danger" id="approveCheck{{plan.id}}">Disapprove</button>`
					)
					$(`#${statusBox}`).html(
						`APPROVED (PDU)`
					)
					$(`#${row}`).attr("class", "table-success")
				}else{
					$(`#${approvalBox}`).html(
						`<button onclick="pduApprovePlan('${planId}', 'approvalBox${planId}', 'statusBox${planId}', 'row${planId}')" class="btn btn-sm btn-block btn-success" id="approveCheck{{plan.id}}">Approve</button>`
					)
					$(`#${statusBox}`).html(
						`APPROVED (HOD)`
					)
					$(`#${row}`).attr("class", "table-primary")
				}
				
			}
		}
	});
}