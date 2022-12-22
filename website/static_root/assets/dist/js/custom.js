$(function(e){
  'use strict'

    /* Data Table */
    $('#example1').DataTable({
        "paging":   false,
        language: {
            searchPlaceholder: 'Search...',
            sSearch: '',
            lengthMenu: '_MENU_',
        }
    });
    /* End Data Table */


    /* Activity */
    var options9 = {
        series: [60, 50, 35],
        chart: {
            height: 345,
            type: 'radialBar',
        },
        plotOptions: {
            radialBar: {
                dataLabels: {
                    name: {
                        fontSize: '22px',
                    },
                    value: {
                        fontSize: '16px',
                        color:'#7c8099',
                    },
                    total: {
                        show: false,
                        label: 'Total',
                        formatter: function(w) {
                            return 249
                        }
                    }
                },
                track: {
                    background: 'rgba(119, 119, 142, 0.2)',
                },
            }
        },
        labels: ['Sales', 'Visits', 'Profit'],
        colors: ['#5569f0', '#f55b39', '#2baf4a'],
    };
    var chart9 = new ApexCharts(document.querySelector("#activity"), options9);
    chart9.render();
    /* End Activity */

    /* Visitors */
    var ctx = $('#visitors');
    ctx.height(310);
    var myChart = new Chart(ctx, {
        type: 'line',
        data : {
            labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            datasets: [
            {
                label: "New Visitors",
                data: [2700,  3500, 2500,  4000,  2300,  3500, 3800],
                backgroundColor: 'transparent',
                borderColor: '#f55b39',
                pointBorderWidth :2,
                pointRadius :5,
                pointHoverRadius :5,
                labelColor:'#f55b39',
                borderWidth: 4,
                pointStyle: 'circle',
                pointBorderColor: '#f55b39',
                pointBackgroundColor: '#f55b39',

            }, {
                label: "Exiting Visitors",
                data: [2500,  3700, 2100,  4400,  1800,  2800, 2500],
                backgroundColor: 'transparent',
                borderColor: '#5569f0',
                pointBorderWidth :2,
                pointRadius :5,
                pointHoverRadius :5,
                borderWidth: 4,
                pointStyle: 'circle',
                pointBorderColor: '#5569f0',
                pointBackgroundColor: '#5569f0',
            }
          ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            legend: {
                display:false,
                labels: {
                    fontColor: '#868ca2'
                }
            },
            tooltips: {
                show: true,
                showContent: true,
                alwaysShowContent: true,
                triggerOn: 'mousemove',
                trigger: 'axis',
                axisPointer:
                {
                    label: {
                        show: false,
                        color: '#868ca2',
                    },
                }
            },

            scales: {
                xAxes: [ {
                    ticks: {
                        fontColor: "#7c8099",
                    },
                    display: true,
                    gridLines: {
                        color:'rgba(119, 119, 142, 0.2)',
                        zeroLineColor: 'rgba(119, 119, 142, 0.03)',
                    }
                } ],
                yAxes: [ {
                    gridLines: {
                        color:'rgba(119, 119, 142, 0.2)',
                        zeroLineColor: 'rgba(119, 119, 142, 0.03)',
                        drawBorder: false,
                        display:false
                    },
                    scaleLabel: {
                        display: false,
                    },
                    ticks: {
                        fontSize: 12,
                        fontColor: '#868ca2',
                        padding: 0,
                        maxRotation: 0,
                        stepSize: 1000,
                        min: 1000,
                        max: 5000
                    },
                } ]
            },
            title: {
                display: false,
            },
            elements: {
                line: {
                    borderWidth: 2
                },
                point: {
                    radius: 0,
                    hitRadius: 10,
                    hoverRadius: 5
                }
            }
        }
    })
    /* End Visitors */

    /*-- Jvector Map -- */
    $('#world-map-markers').vectorMap({
        map : 'world_mill_en',
        scaleColors : ['#5d3ced', 'rgba(119, 119, 142, 0.3)'],
        normalizeFunction : 'polynomial',
        hoverOpacity : 0.7,
        hoverColor : false,
        regionStyle : {
            initial : {
                fill : 'rgba(119, 119, 142, 0.3)'
            }
        },
        markerStyle: {
            initial: {
                r: 6,
                'fill': '#5d3ced',
                'fill-opacity': 0.9,
                'stroke': '#fff',
                'stroke-width' : 2.5,
            },

            hover: {
                'stroke': '#fff',
                'fill-opacity': 1,
                'stroke-width': 1.5
            }
        },
        backgroundColor : 'transparent',
        markers : [{
            latLng : [-23.533773, -46.625290],
            name : 'Brazil'
        }, {
            latLng : [55.751244, 37.618423],
            name : 'Russia'
        }, {
            latLng : [52.237049, 21.017532],
            name : 'Poland'
        },  {
            latLng : [51.213890, -110.005470],
            name : 'Canada'
        },{
            latLng : [20.5937, 78.9629],
            name : 'India'
        }]
    });
    /*-- End Jvector Map -- */
});

