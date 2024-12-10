/* ========================================
 *
 * Copyright YOUR COMPANY, THE YEAR
 * All Rights Reserved
 * UNPUBLISHED, LICENSED SOFTWARE.
 *
 * CONFIDENTIAL AND PROPRIETARY INFORMATION
 * WHICH IS THE PROPERTY OF your company.
 *
 * ========================================
*/
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include "project.h"

#define RX_BUFFER_SIZE 64
char rxBuffer[RX_BUFFER_SIZE];
uint8_t rxIndex = 0;

#define SPEED_CONSTANT 1256
#define DESIRED_SPEED 4

#define PWM_BASE 50
#define KP 50 // 150
#define KI 5  // 15

#define MAX_PWM 200
#define MIN_PWM 2

#define true 1
#define false 0
#define forward 0
#define backward 1

// Steering
#define SERVO_CENTER 120
#define SERVO_MAX 150
#define SERVO_MIN 90
volatile unsigned int servoPosition = 120;

volatile double integral = 0;  // Integral term
volatile double speedTarget = 0;
volatile unsigned int motionState = 0;

// Box status
volatile unsigned int boxesInSystem = 0;
volatile unsigned int lowerOccupied = false;

// Stacker PWM parameters
#define GATE_OPEN 25
#define GATE_CLOSED 4
#define PUSHER_IN 8
#define PUSHER_OUT 19
#define HEADBAND_UP 7
#define HEADBAND_DOWN 17

// Servo parameters
#define SERVO_DELAY 800

uint16 new_time;
uint16 old_time;
uint16 elapsed;
double speed;
double PWM;

char strbuf[16];

void GradualHeadband(int start, int end, int steps, int delay){
    
    for(int i = start; i >=end; i+=(end - start)/steps) {
        Headband_PWM_WriteCompare(i);
        CyDelay(delay/steps);
    }
    Headband_PWM_WriteCompare(end);
}

void RaiseBoxes(){
    if(lowerOccupied){
        Gate_PWM_WriteCompare(GATE_CLOSED);
        CyDelay(SERVO_DELAY);
        UART_PutString("Gate Closed\n");
        Headband_PWM_WriteCompare(HEADBAND_UP);
        CyDelay(SERVO_DELAY);
        UART_PutString("Headband Up\n");
        Pusher_PWM_WriteCompare(PUSHER_OUT);
        CyDelay(SERVO_DELAY);
        UART_PutString("Pusher Out\n");
        Gate_PWM_WriteCompare(GATE_OPEN);
        CyDelay(SERVO_DELAY);
        UART_PutString("Gate Open\n");
        Headband_PWM_WriteCompare(HEADBAND_DOWN);
        CyDelay(SERVO_DELAY);
        UART_PutString("Headband Down\n");
        
        lowerOccupied = false;
        UART_PutString("1");
    } else {
        UART_PutString("0");
    }
}

void LowerBoxes(){
    if (!lowerOccupied) {
        Gate_PWM_WriteCompare(GATE_CLOSED);
        CyDelay(SERVO_DELAY);
        UART_PutString("Gate Closed\n");  
        Headband_PWM_WriteCompare(HEADBAND_UP);
        CyDelay(SERVO_DELAY);
        UART_PutString("Headband Up\n");
        Pusher_PWM_WriteCompare(PUSHER_IN);
        CyDelay(SERVO_DELAY);
        UART_PutString("Pusher In\n");
        // GradualHeadband(HEADBAND_UP, HEADBAND_DOWN, 10, SERVO_DELAY);
        Headband_PWM_WriteCompare(HEADBAND_DOWN);
        CyDelay(SERVO_DELAY);
        UART_PutString("Headband Down\n");
        Gate_PWM_WriteCompare(GATE_OPEN);
        CyDelay(SERVO_DELAY);
        UART_PutString("Gate Open\n");
        UART_PutString("1");
        lowerOccupied = true;
    } else {
        UART_PutString("0");
    }
}

unsigned int PullBoxIn(){
    if (!lowerOccupied) {
        Pusher_PWM_WriteCompare(PUSHER_IN);
        CyDelay(SERVO_DELAY);
        /*
        drive forward
        stop
        */
        UART_PutString("1");
        boxesInSystem++;
        lowerOccupied = true;
    } else {
        UART_PutString("0");
    }
    
    return !lowerOccupied;
}

unsigned int PushBoxOut() {
    if (lowerOccupied) {
        Pusher_PWM_WriteCompare(PUSHER_OUT);
        CyDelay(SERVO_DELAY);
        boxesInSystem--;
        UART_PutString("1");
        lowerOccupied = false;
    } else {
        UART_PutString("0");
    }
    
    return lowerOccupied;
}

// Handling instructions
void HandleInstruction(const char* command, const char* param){
    if(strcmp(command, "FORWARD") == 0){
        char* ret;
        speedTarget = (unsigned int) strtoul(param, &ret, 10);
        PWM_Back_WriteCompare (255);
        if(speedTarget > 0){
            PWM_Fwd_WriteCompare ((uint8) 200);
        } else {
            PWM_Fwd_WriteCompare (255);
        }
        motionState = 0;
        UART_PutString("1");
    }
    
    if(strcmp(command, "BACK") == 0){
        char* ret;
        speedTarget = (unsigned int) strtoul(param, &ret, 10);
        PWM_Fwd_WriteCompare (PWM_Fwd_ReadPeriod());
        if(speedTarget > 0){
            PWM_Back_WriteCompare ((uint8) 200);
        } else {
            PWM_Back_WriteCompare (255);
        }
        motionState = 1;
        UART_PutString("1");
        
    }
    
    if(strcmp(command, "STEER") == 0){
        char* ret;
        unsigned int newPosition = (unsigned int) strtoul(param, &ret, 10);
        if(newPosition > SERVO_MAX){
            newPosition = SERVO_MAX;
        } else if (newPosition < SERVO_MIN) {
            newPosition = SERVO_MIN;
        }
        Steering_PWM_WriteCompare(newPosition);
        UART_PutString("1");
    }
    
    /*if(strcmp(command, "RIGHT") == 0){
        char* ret;
        int newPosition = servoPosition + (unsigned int) strtoul(param, &ret, 10);
        if(newPosition > SERVO_MAX){
            newPosition = SERVO_MAX;
        } else if (newPosition < SERVO_MIN) {
            newPosition = SERVO_MIN;
        }
        servoPosition = (unsigned int)newPosition;
        Steering_PWM_WriteCompare(servoPosition);
        UART_PutString("1");
    }
    if(strcmp(command, "LEFT") == 0){
        char* ret;
        int newPosition = servoPosition - (unsigned int) strtoul(param, &ret, 10);
        if(newPosition > SERVO_MAX){
            newPosition = SERVO_MAX;
        } else if (newPosition < SERVO_MIN) {
            newPosition = SERVO_MIN;
        }
        servoPosition = (unsigned int)newPosition;
        Steering_PWM_WriteCompare(servoPosition);
        UART_PutString("1");
    }
    */
    if(strcmp (command, "LIFT") == 0) {
        if (strcmp(param, "UP") == 0) {
            RaiseBoxes();
        }
        if (strcmp(param, "DOWN") == 0) {
            LowerBoxes();
        }
    }
    if(strcmp (command, "EXCHANGE") == 0) {
        if (strcmp(param, "IN") == 0) {
            unsigned int status = PullBoxIn();
            // send back failure if false
        }
        if (strcmp(param, "OUT") == 0) {
            unsigned int status = PushBoxOut();
            // send back failure if false
        }
    }
}




CY_ISR(RX_vector) {
    while (UART_GetRxBufferSize() > 0) {
        char receivedData = UART_ReadRxData();
        
        // End of command handling
        if(receivedData == '\n'){
            rxBuffer[rxIndex] = '\0';
            
            // Parse the command
            char *command = NULL;
            char *param = NULL;
            
            command = strtok(rxBuffer, " ");
            if (command) {
                param = strtok(NULL, " ");
            }
            
            HandleInstruction(command, param);
    
            rxIndex = 0;
            } else if (rxIndex < RX_BUFFER_SIZE - 1) { // Prevent buffer overflow
                rxBuffer[rxIndex++] = receivedData;
            } else {
                // Buffer overflow: reset the buffer
                rxIndex = 0;
            }
    }
}

CY_ISR(HE_vector){
    // Read the timer value
    uint16_t timerValueRaw = Timer_ReadCapture();
    double timerValue = (double) timerValueRaw;
    timerValue = 65535 - timerValue;
   
    Timer_ReadStatusRegister();
    // Reset the timer
    Timer_WriteCounter(65535);
    //average the times between
    double averageTime = timerValue;
        
    //find current speed
    double currentSpeed = SPEED_CONSTANT / ((double) averageTime);
    
    
    
    //find error
    double error = speedTarget - currentSpeed;

    //update integral term
    integral += error;

    //calculate PWM
    double PWM = KP * error + KI * integral + PWM_BASE;

    //set PWM
    if(PWM > MAX_PWM) {
        PWM = MAX_PWM;
    } else if(PWM < MIN_PWM) {
        PWM = MIN_PWM;
    }
    
    PWM = 255 - PWM;
    
    if (motionState == 0) {
        PWM_Fwd_WriteCompare(PWM);
        PWM_Back_WriteCompare(255);
        
    } else if (motionState == 1) {
        PWM_Back_WriteCompare(PWM);
        PWM_Fwd_WriteCompare(255);
    }
    
    
    // Print timer value, current speed, and PWM to UART
    char output[48];
    sprintf(output, "Timer:%d,Speed:%d,PWM:%d, Motion State: %d\n\r", 
            (int)timerValue, 
            (int)(currentSpeed * 100),
            (int)PWM,
            (int)motionState);
    UART_PutString(output);
    
}

int main(void)
{
    CyGlobalIntEnable; /* Enable global interrupts. */

    /* Place your initialization/startup code here (e.g. MyInst_Start()) */
    // Transmission and Control
    UART_Start();
    RX_ISR_Start();
    RX_ISR_SetVector(RX_vector);
    
    // Steering
    Steering_PWM_Start();
    
    // Speed Control
    Timer_Start();
    PWM_Fwd_Start();
    PWM_Back_Start();
    HE_ISR_Start();
    HE_ISR_SetVector(HE_vector);
    
    // Stacker
    Headband_PWM_Start();
    Gate_PWM_Start();
    Pusher_PWM_Start();
    
    // Initialization
    UART_PutString("initialized /r/n");
    
    Steering_PWM_WriteCompare(120);
    speedTarget = 0;
    
    // Stacker initial conditions
    Gate_PWM_WriteCompare(GATE_OPEN);
    Headband_PWM_WriteCompare(HEADBAND_DOWN);
    Pusher_PWM_WriteCompare(PUSHER_OUT);
    
    // H Bridge initial conditions
    PWM_Fwd_WriteCompare (PWM_Fwd_ReadPeriod());
    PWM_Back_WriteCompare (PWM_Back_ReadPeriod());
    
    PWM_Fwd_WriteCompare(200);
    
    for(;;)
    {
        /* Place your application code here. */
      
    }
}

/* [] END OF FILE */
