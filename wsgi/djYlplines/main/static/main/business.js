/**
 * Created by KaTaLYSTXV on 3/29/16.
 */
var chart1
$(function() {
    chart1 = new Highcharts.StockChart({
        chart: {
            renderTo: 'container'
        },
        series: [
            {
                'name': 'ylpline rating',
                'type': 'spline',
                'data': ylpline_ratings,
            },
            {
                'name': 'review rating',
                'type': 'scatter',
                'data': review_ratings,
            }
        ],
        plotOptions: {
            series: {
                allowPointSelect: true
            }
        }
    })
   /* $('#container').Highcharts.StockChart({
        chart: chart,
        title: title,
        xAxis: xAxis,
        yAxis: yAxis,
        series: series
    });*/
});
     /* chart1 = new Highcharts.StockChart({
         chart: {
            renderTo: 'container'
         },
         rangeSelector: {
            selected: 1
         },
         series: [{
            name: 'USD to EUR',
            data: [1,2,3,4,5] // predefined JavaScript array
         }]
      });
   });
*/
/*$(function () {
    $('#container').highcharts({
        chart: {
            type: 'bar'
        },
        title: {
            text: 'Fruit Consumption'
        },
        xAxis: {
            categories: ['Apples', 'Bananas', 'Oranges']
        },
        yAxis: {
            title: {
                text: 'Fruit eaten'
            }
        },
        series: [{
            name: 'Jane',
            data: [1, 0, 4]
        }, {
            name: 'John',
            data: [5, 7, 3]
        }]
    });
});*/
