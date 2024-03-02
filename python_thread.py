import threading
import cobaProsesMqtt
import plot_streamlit

if __name__ == "__main__":
    # Start MQTT data retrieval thread
    mqtt_thread = threading.Thread(target=cobaProsesMqtt.run_mqtt_data_retrieval)
    mqtt_thread.start()

    # Run the Dash server for plotting
    plot_streamlit.app.run_server(debug=True)