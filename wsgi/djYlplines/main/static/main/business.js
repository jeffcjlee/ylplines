/**
 * ylplines - Clarity for Yelp
 * Copyright (C) 2016  Jeff Lee
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 * */
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
                'color': '#0000FF',
                'data': ylpline_ratings,
            },
            {
                'name': 'review rating',
                'type': 'scatter',
                'color': 'rgba(10,200,90,0.15)',
                'data': review_ratings,
            }
        ],
        plotOptions: {
            series: {
                allowPointSelect: true
            }
        }
    })
});