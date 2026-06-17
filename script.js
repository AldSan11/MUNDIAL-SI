$("#btnPredecir").click(function(){

    let grupo = $("#grupo").val();

    $("#resultado").html("<p>Cargando predicción...</p>");

    $.ajax({
        url: "/predecir",
        method: "GET",
        data: {
            grupo: grupo
        },
        success: function(datos){

            let html = "";

            html += `<h2>Predicción Grupo ${datos.grupo}</h2>`;

            html += `
            <table>
                <tr>
                    <th>Posición</th>
                    <th>Equipo</th>
                    <th>Puntos</th>
                </tr>
            `;

            datos.tabla.forEach(function(equipo, index){

                html += `
                <tr>
                    <td>${index + 1}</td>
                    <td>${equipo.equipo}</td>
                    <td>${equipo.puntos}</td>
                </tr>
                `;

            });

            html += "</table>";

            html += "<h3>Clasificados previstos:</h3>";

            datos.clasificados.forEach(function(equipo){
                html += `<p>✅ ${equipo.equipo}</p>`;
            });

            $("#resultado").html(html);
        },
        error: function(){
            $("#resultado").html("<p>Error al conectar con el predictor.</p>");
        }
    });

});