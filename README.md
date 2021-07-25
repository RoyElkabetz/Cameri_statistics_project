# Cameri_statistics_project
>Scraping live wave measurements data measured along the coasts of Israel from the [Cameri Haifa](https://www.israports.co.il//_layouts/15/wave/haifaw-ipa.html) and [Cameri Ashdod](https://www.israports.co.il//_layouts/15/wave/ashdodw-ipa.html) websites.
>The data is saved localy and is updated from time to time into the [`data`](/data) folder.
>The reason for this project is to collect long time wave measurements data for future Deep Learning based wave forecasting.


## Scraped Data
Here is an example of wave measurements data collected from [Cameri's](https://www.israports.co.il//_layouts/15/wave/haifaw-ipa.html) buoy along Haifa, Israel coast.

| TimeGMT	           | Hmax meter	|Hs meter	| H1/3 meter | Direction deg | Tav sec | Tz sec |	Tp sec | Temperature C |
| -------------------|:----------:|:-------:|:----------:|:-------------:|:-------:|:------:|:------:|:-------------:|
| 2021-07-19 00:15:00|	0.95  	  | 0.66	  | 0.61	     | 270	         | 5	     | 4.5	  | 7.1	   | 29.85         |
| 2021-07-19 00:45:00|	1.02  	  | 0.61	  | 0.55	     | 269	         | 4.7	   | 4.5	  | 7.1	   | 29.85         |
| 2021-07-19 01:15:00|	1.06  	  | 0.68	  | 0.63	     | 270	         | 5.2	   | 4.9	  | 7.1	   | 29.85         |

