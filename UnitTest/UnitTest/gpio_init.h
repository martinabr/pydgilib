/*
 * gpio_init.h
 *
 * Created: 2019-03-19 16:47:35
 *  Author: erikw_000
 */ 


#ifndef GPIO_INIT_H_
#define GPIO_INIT_H_

#define INIT_GPIO
#define INIT_LED

#ifdef INIT_GPIO
#define GPIO_HIGH true
#define GPIO_LOW false

#define DGI_GPIO0 GPIO(GPIO_PORTA, 10)
#define DGI_GPIO1 GPIO(GPIO_PORTA, 11)
#define DGI_GPIO2 GPIO(GPIO_PORTA, 23)
#define DGI_GPIO3 GPIO(GPIO_PORTA, 27)
#endif

#ifdef INIT_LED
#define LED_ON false
#define LED_OFF true

#define LED0 GPIO(GPIO_PORTA, 7)
#endif

void gpio_init(void);

#endif /* GPIO_INIT_H_ */