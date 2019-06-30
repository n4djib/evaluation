
// <p>Date/Time: <span id="datetime"></span></p>
// { % include "_datetime.js" %}


var dt_elem = document.getElementById("datetime");

if (dt_elem !== null)
    dt_elem.innerHTML = get_current_datetime();

function get_current_datetime() {
	var d = new Date(),
	    minutes = d.getMinutes().toString().length == 1 ? '0'+d.getMinutes() : d.getMinutes(),
	    hours = (d.getHours()-1).toString().length == 1 ? '0'+(d.getHours()-1) : (d.getHours()-1),
	    ampm = d.getHours() >= 12 ? 'pm' : 'am',
	    // months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
	    // months = ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Dec'],
	    months = ['janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'],

	    // days = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'],
	    // days = ['Dim','Lun','Mar','Mer','Jeu','Ven','Sam'],
	    days = ['Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'],

	    day_str = d.getDate().toString().length == 1 ? '0'+(d.getDate()) : (d.getDate()),
	    month_str = (d.getMonth()+1).toString().length == 1 ? '0'+(d.getMonth()+1) : (d.getMonth()+1);

	var msg = 'Imprimer : '
	return msg + days[d.getDay()]
		// +' '+months[d.getMonth()]
		+' '+day_str+'/'+month_str+'/'+d.getFullYear()
		+' '+hours+':'+minutes
		// +ampm
		;
}




