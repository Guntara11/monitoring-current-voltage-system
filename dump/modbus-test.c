#include "base.h"

int read_data_modbus(int slave_id, int reg_address, float *val){
    pthread_mutex_lock(&mutex);
    
    modbus_t *ctx;
    uint16_t reg[2];
    int rc;

    // Floor check
    if(slave_id < 8){  // Floor 2
        ctx = modbus_new_tcp(IP_F2, PORT);
    }else if((slave_id > 7) && (slave_id < 14)){  // Floor 3
        ctx = modbus_new_tcp(IP_F3, PORT);
    }else if((slave_id > 13) && (slave_id < 32)){  // Floor 5
        ctx = modbus_new_tcp(IP_F5, PORT);
    }else if((slave_id > 31) && (slave_id < 52)){  // Floor 6
        ctx = modbus_new_tcp(IP_F6, PORT);
    }else if((slave_id > 51) && (slave_id < 57)){  // Floor 1
        ctx = modbus_new_tcp(IP_F1, PORT);
    }
    else{ // Not in a range
        // Error handler
        pthread_mutex_unlock(&mutex);
        return -1;
    }

    // ctx = modbus_new_tcp("192.168.10.3", 502);
    rc = modbus_set_slave(ctx, slave_id);
    if(rc < 0){
        printf("Error set slave\n");
        pthread_mutex_unlock(&mutex);
        return -1;
    }
    rc = modbus_connect(ctx);
    if(rc < 0){
       printf("Error connect to modbus\n");
       pthread_mutex_unlock(&mutex);
       return -1;
    }

    rc = modbus_read_registers(ctx, reg_address, 2, reg);
    if (rc == -1) {
        printf("Cannot read\n");
        pthread_mutex_unlock(&mutex);
        // handle error
        return -1;
    }
    else {
        // use the data in the reg array
        uint32_t value = (reg[0] << 16) + reg[1];
        float f;
        memcpy(&f, &value, sizeof(value));
        // debug
        // printf("Read value: %.3f\n", f);
        *val = f;
    }

    modbus_close(ctx);
    modbus_free(ctx);

    usleep(10000);

    pthread_mutex_unlock(&mutex);

    return 0;
}