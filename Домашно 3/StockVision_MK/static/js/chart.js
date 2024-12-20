const getDataFromAPI = async () => {
    const symbol = document.getElementById('tvchart').getAttribute('symbol');
    try {
        const response = await fetch(`http://127.0.0.1:8000/api/stock-data/?symbol=${symbol}&start_date=2014-01-01&end_date=2024-12-31`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        console.log('Raw Data from API:', data);
        return data;
    } catch (error) {
        console.error('Error fetching data:', error);
        return [];
    }
};

const renderChart = async () => {
    const chartProperties = {
        width: 1100,
        height: 600,
        timeScale: {
            timeVisible: true,
            secondsVisible: false,
        },
    };

    const domElement = document.getElementById('tvchart');
    const chart = LightweightCharts.createChart(domElement, chartProperties);
    const candleSeries = chart.addCandlestickSeries();

    const apiData = await getDataFromAPI();

    const cleanedData = apiData
        .map(d => {
            if (d.date && d.open && d.high && d.low && d.close) {
                return {
                    time: new Date(d.date).getTime() / 1000,
                    open: parseFloat(d.open),
                    high: parseFloat(d.high),
                    low: parseFloat(d.low),
                    close: parseFloat(d.close),
                };
            } else {
                console.warn('Invalid data entry detected and skipped:', d);
                return null;
            }
        })
        .filter(d => d !== null);

    const sortedData = cleanedData.sort((a, b) => a.time - b.time);

    const uniqueData = sortedData.filter((item, index, self) =>
        index === self.findIndex((t) => t.time === item.time)
    );

    console.log('Unique Sorted Data for Chart:', uniqueData);

    if (uniqueData.length > 0) {
        candleSeries.setData(uniqueData);
    } else {
        console.log('No valid data available for the chart.');
    }
};

renderChart();
