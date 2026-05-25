# Projeto IoT - Monitor de Umidade do Solo

O sensor de umidade faz a leitura em um range de 0 a 1023, sendo 0 solo seco e 1023 solo úmido. Com isso é criado uma função que lê a porta do serial e retorna somente o valor da umidade isolado, essa função é chamada de ler_porta_serial(). A função api_dados() faz a leitura do valor da umidade atual e retorna em formato JSON para o front-end. 

# IoT Project - Soil Moisture Monitor

The soil moisture sensor reads in a range of 0 to 1023, with 0 being dry soil and 1023 being wet soil. With this, a function is created that reads the serial port and returns only the isolated humidity value, this function is called ler_porta_serial(). The api_dados() function reads the current humidity value and returns it in JSON format to the front-end. 
