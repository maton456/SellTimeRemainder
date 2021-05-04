import json
import boto3
import datetime
import glob
import os
import mplfinance as mpf  # takes 1 sec
import pandas as pd


def plot_price_dairy(card_name, date_list, price_list, S3_bucket_name):
    #print('plot_price_dairy()')

    # Initialize dataframe
    time_sr = pd.Series(date_list)
    time_sr2 = pd.to_datetime(time_sr, format='%Y-%m-%d')
    df = pd.DataFrame({'date': time_sr2,
                       'Open': price_list,
                       'High': price_list,
                       'Low': price_list,
                       'Close': price_list,
                       'Volume': price_list,
                       })
    df = df.set_index('date')
    df = df.sort_index()
    #print(df)

    # Plot and save in local
    save_dir = '/tmp/dairy_'
    #os.makedirs(save_dir, exist_ok=True)
    save_filename = save_dir + card_name + '.png'
    mpf.plot(df, type='line', mav=(5, 25),
        show_nontrading=True,
        datetime_format='%Y/%m/%d',
        title=card_name,
        savefig=save_filename
    )
    print('Save in temporary local dir: ' + save_filename)

    # Upload to S3
    s3 = boto3.resource('s3')
    save_object_path = save_filename.replace(save_dir, 'png/dairy/')
    s3.Bucket(S3_bucket_name).upload_file(save_filename, save_object_path)
    print('Upload to S3 bucket: ' + S3_bucket_name + ', path: ' + save_object_path)

    return True


def plot_price_weekly(card_name, date_list, price_list, S3_bucket_name):
    #print('plot_price_weekly()')

    # Convert dairy into weekly
    num_date = len(date_list)
    num_left_date = num_date
    week_begin_date = datetime.datetime.strptime(date_list[0], '%Y-%m-%d')
    week_dict = {
        'date': [],
        'Open': [],
        'High': [],
        'Low': [],
        'Close': [],
        'Volume': [],
    }
    tmp_High = 0
    tmp_Low = 1000000
    last_flag = False
    for date, price in zip(date_list, price_list):
        #print(date, price)
        # If last item
        num_left_date -= 1
        if num_left_date == 0:
            last_flag = True

        date_dt = datetime.datetime.strptime(date, '%Y-%m-%d')
        week_elapsd_day = (date_dt - week_begin_date).days
        if week_elapsd_day >= 7:
            week_begin_date = date_dt
            week_elapsd_day = 0
        
        if week_elapsd_day == 0:
            week_dict['date'].append(date)
            week_dict['Open'].append(price)
            tmp_High = 0
            tmp_Low = 1000000
        if price > tmp_High:
            tmp_High = price
        if price < tmp_Low:
            tmp_Low = price
        if week_elapsd_day == 6 or last_flag:
            week_dict['High'].append(tmp_High)
            week_dict['Low'].append(tmp_Low)
            week_dict['Close'].append(price)
            week_dict['Volume'].append(1)
        if last_flag:
            break

    # Initialize dataframe
    time_sr = pd.Series(week_dict['date'])
    time_sr2 = pd.to_datetime(time_sr, format='%Y-%m-%d')
    df = pd.DataFrame({'date': time_sr2,
                       'Open': week_dict[('Open')],
                       'High': week_dict[('High')],
                       'Low': week_dict[('Low')],
                       'Close': week_dict[('Close')],
                       'Volume': week_dict[('Volume')],
                       })
    df = df.set_index('date')
    df = df.sort_index()
    #print(df)

    # Plot and save in local
    save_dir = '/tmp/weekly_'
    #os.makedirs(save_dir, exist_ok=True)
    save_filename = save_dir + card_name + '.png'
    mpf.plot(df, type='candle', mav=(5, 25),
        show_nontrading=True,
        datetime_format='%Y/%m/%d',
        title=card_name,
        savefig=save_filename
    )
    print('Save in temporary local dir: ' + save_filename)

    # Upload to S3
    s3 = boto3.resource('s3')
    save_object_path = save_filename.replace(save_dir, 'png/weekly/')
    s3.Bucket(S3_bucket_name).upload_file(save_filename, save_object_path)
    print('Upload to S3 bucket: ' + S3_bucket_name + ', path: ' + save_object_path)

    return True


def clear_tmp_dir():
    for p in glob.glob('/tmp/' + '*'):
        if os.path.isfile(p):
            os.remove(p)
    print('Clear /tmp/*')


def lambda_handler(event, context):
    # TODO implement
    bucket_name = 'highso.com'

    for record in event['Records']:
        if record['eventName'] != "MODIFY":
            print('This record is not MODIFY event.')
            continue
        card_name = record['dynamodb']['NewImage']['URL']['S'].split('/')[-2]
        print('card_name: ' + card_name)
        prices_dict = record['dynamodb']['NewImage']['Prices']['M']
        #print('prices_dict: ', prices_dict)

        date_list = []
        price_list = []
        for key, value in prices_dict.items():
            date_list.append(key)
            price_list.append(int(value['N']))
        #print('date_list: ', date_list)
        #print('price_list: ', price_list)
        
        # Sort with date_list
        tmp_zip = zip(date_list, price_list)
        tmp_zip_sorted = sorted(tmp_zip, key=lambda x: x[0])
        #print('tmp_zip_sorted: ', tmp_zip_sorted)
        date_list_sorted, price_list_sorted = zip(*tmp_zip_sorted)
        #print('date_list_sorted: ', date_list_sorted)
        #print('price_list_sorted: ', price_list_sorted)

        # Plot and upload to S3
        plot_price_dairy(card_name, date_list_sorted, price_list_sorted, S3_bucket_name=bucket_name)  # takes 1.6sec
        plot_price_weekly(card_name, date_list_sorted, price_list_sorted, S3_bucket_name=bucket_name)  # takes 2.2sec

        # Clear Lambda tmp dir
        clear_tmp_dir()

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }