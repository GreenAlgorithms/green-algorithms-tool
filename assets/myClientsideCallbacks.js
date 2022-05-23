window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        reset_function: function(clicks) {
            if (clicks > 0) {
                window.location.href = "https://www.green-algorithms.org";
                // window.location.href = "http://127.0.0.1:8050/";
                // DEBUGONLY remove that before releasing
                return String(clicks)
            } else {
                return 'Nope '+String(clicks)
            }
        }
    }
});