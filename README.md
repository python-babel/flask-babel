Flask ICU
=========

[![Build Status](https://travis-ci.org/beavyHQ/flask-icu.svg?branch=retrofit-for-pyicu)](https://travis-ci.org/beavyHQ/flask-icu)

Implements i18n and l10n support for Flask using the industry standard
ICU.

Please consult these links in order to better understand ICU syntax:  
* [http://userguide.icu-project.org/formatparse/messages](http://userguide.icu-project.org/formatparse/messages)
* http://formatjs.io/guides/message-syntax/

This library supports the following formatting methods:

   * **format()**
 ```
 format('You have {num} messages.', {'num': 3})
 # => You have 3 messages.
 ```
   * **format_date()**  
 ```python
 format_date(datetime(2010, 4, 12, 13, 46))
 # => Apr 12, 2010
 ```
   * **format_time()**  
```python
 format_time(datetime(2010, 4, 12, 13, 46))
 # => 1:46:00 PM
 ```
   * **format_datetime()**   
 ```python
 format_datetime(datetime(2010, 4, 12, 13, 46))
 # => Apr 12, 2010, 3:46:00 PM
 ```
   * **format_number()**  
 ```python
 format_number(1099)
 # => 1,099
 ```
   * **format_decimal()**  
 ```python
 format_decimal(Decimal('1010.99'))
 # => 1,010.99
 ```
   * **format_currency()**  
 ```python
 format_currency(1099, 'ILS')
 # => ₪1,099.00
 ```
   * **format_scientific()**
 ```python
 format_scientific(10000)
 # => 1E4
 ```
   * **format_percent()**  
 ```python
 format_percent(0.19)
 # => 19%
 ```


Steps for extracting messages for tests:  
1. Use pybabel to extract messages from tests file   
2. Initialize translation files  
3. Use po2json to generate json translation files  
