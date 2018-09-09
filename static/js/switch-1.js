        $(document).ready(function(e) {
             $('input').lc_switch();
        });
            
        $('body').delegate('.lcs_check', 'lcs-statuschange', function() {
            var status = ($(this).is(':checked')) ? 'checked' : 'unchecked';
            console.log('field changed status: '+ status );
            var req = new XMLHttpRequest();
            req.open('GET', 'http://192.168.24.6:8080/rest/items/Temperatura/state', false);
            req.send(null);
            if (req.status == 200) {
                console.log(req.responseText);
                console.log('Conseguido');
            }
            else
            {
                console.log('Error');
            }
        });
            
        // triggered each time a field is checked
        $('body').delegate('.lcs_check', 'lcs-on', function() {
            console.log('field is checked');
        });
