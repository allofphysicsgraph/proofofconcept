
# the order of installation matters for these two :(
#get_ipython().system('pip install python-geoip-geolite2')
#get_ipython().system('pip install python-geoip-python3')

import shutil  # move and copy files
import datetime
import pandas
import re # https://docs.python.org/3/library/re.html
import time
import matplotlib.pyplot as plt
from geoip import geolite2 # https://pythonhosted.org/python-geoip/
import os
import logging

logger = logging.getLogger(__name__)


def extract_username(msg):
    """
        Helper functions should not have trace turned on
        because the logger is triggered per dataframe row
    >>> 
    """
#    logger.info('[trace]')
    if msg.startswith('Failed password for invalid user '):
        return msg.replace('Failed password for invalid user ','').split(' ')[0]
    elif msg.startswith('Failed password for '):
        return msg.replace('Failed password for ','').split(' ')[0]
    elif msg.startswith('Invalid user '):
        return msg.replace('Invalid user ','').split(' ')[0]
    else:
        return None

def extract_ip(msg):
    """
        Helper functions should not have trace turned on
        because the logger is triggered per dataframe row
    >>> 
    """
#    logger.info('[trace]')

# ### append IP as column in df
    res = re.findall('(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.'+
                     '(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.'+
                     '(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.'+
                     '(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])',msg)
    if len(res)==0:
        return None
    elif len(res)==1:
        return '.'.join(res[0])
    else:
        raise Exception(res)

#def country_if_ip(ip, country_code_df):
#    """
#    >>> 
#    """
#    logger.info('[trace]')
#    # ## IP to country code using library, then country code to name using lookup table
#    if ip:
#        match = geolite2.lookup(ip)
#        if match:
#            return country_code_df[country_code_df['country code']==match.country]['name'].values[0]
#        else:
#            return None
#    else:
#        return None


def auth_log_to_df(path_to_auth_log, path_to_country_code_table):
    """
    >>> auth_log_to_df('logs/auth.log', 'iso3166.csv')
    """
    logger.info('[trace]')
    # download country code lookup table from https://dev.maxmind.com/geoip/legacy/codes/iso3166/
    # https://dev.maxmind.com/static/csv/codes/iso3166.csv
    country_code_df = pandas.read_csv(path_to_country_code_table, header=None, names=['country code', 'name'])

    def country_if_ip(ip):
        """
        Helper functions should not have trace turned on
        because the logger is triggered per dataframe row
        >>> 
        """
#        logger.info('[trace]')
        # ## IP to country code using library, then country code to name using lookup table
        if ip:
            match = geolite2.lookup(ip)
            if match:
                return country_code_df[country_code_df['country code']==match.country]['name'].values[0]
            else:
                return None
        else:
            return None
        return None


    if not os.path.exists(path_to_auth_log):
        with open('auth.log', 'r') as f:
            lines = f.readlines()
        logger.debug('used local auth.log')
    else:
        with open(path_to_auth_log, 'r') as f:
            lines = f.readlines()

    logger.debug('read in auth.log')

    # ## convert list of lines into a list of dicts suitable for a Pandas dataframe

    list_of_dicts = []
    for indx, line in enumerate(lines):
        line_as_dict = {}

        # https://security.stackexchange.com/questions/18207/security-of-log-files-injecting-malicious-code-in-log-files/18209
        line = line.replace('\x00','') # there was a bad character on `lines[6615]`

        line_as_dict['date time'] = line[0:15]
        line_as_list = line[16:].strip().split(' ')

        line_as_dict['server name'] = line_as_list[0].strip()
        if '[' in line_as_list[1]: # https://serverfault.com/a/526151
            line_as_dict['service name'] = line_as_list[1].split('[')[0].strip()
            line_as_dict['pid'] = line_as_list[1].split('[')[1].replace(']:','').strip()
        else:
            line_as_dict['service name'] = line_as_list[1].strip()
        line_as_dict['message'] = ' '.join(line_as_list[2:])
        list_of_dicts.append(line_as_dict)

    df = pandas.DataFrame(list_of_dicts)

    # convert `date time` string to Python datetime
    # https://strftime.org/
    df['datetime'] = pandas.to_datetime('2020 ' + df['date time'], format='%Y %b %d %H:%M:%S')
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.drop.html
    df.drop('date time', inplace=True, axis=1)

    # ### add username as column in df
    df['username'] = df['message'].apply(extract_username)

    df['ip'] = df['message'].apply(extract_ip)

    df['country'] = df['ip'].apply(country_if_ip)

    df['year'] = pandas.DatetimeIndex(df['datetime']).year
    df['month'] = pandas.DatetimeIndex(df['datetime']).month
    df['day'] = pandas.DatetimeIndex(df['datetime']).day

    return df


def plot_username_distribution(df,path_to_save_to: str,output_filename: str) -> None:
    """
    >>> output_filename = 'unique_usernames_'
    >>> path_to_save_to = "/home/appuser/app/static/"
    >>> plot_username_distribution(df,path_to_save_to)
    """
    logger.info('[trace]')
    user_name_series = df['username'].value_counts().head(20)

    # https://stackoverflow.com/a/8228808/1164295
    plt.close('all')
    # https://stackoverflow.com/a/16014873/1164295
    plt.bar(range(len(user_name_series)), list(user_name_series.values), align='center')
    _=plt.xticks(range(len(user_name_series)), list(user_name_series.index), rotation='vertical')
    _=plt.ylabel('number of login attempts')
    _=plt.xlabel('user name attempted')
    plt.savefig(output_filename, format='png', bbox_inches = "tight")
    shutil.move(output_filename, path_to_save_to + output_filename)
    return


# # separate times

def plot_ip_vs_time(df,path_to_save_to: str,output_filename: str) -> None:
    """
    >>> output_filename = 'unique_IP_address_per_day_'
    >>> path_to_save_to = "/home/appuser/app/static/"
    >>>
    """
    logger.info('[trace]')

    # https://stackoverflow.com/a/8228808/1164295
    plt.close('all')

    gb = df.groupby([(df['year']),(df['month']), (df['day'])]).nunique()['ip'].plot(kind='bar')
    _=plt.ylabel('number of unique IP addresses')
    _=plt.title('IP addresses observed per day')

    plt.savefig(output_filename, format='png', bbox_inches = "tight")
    shutil.move(output_filename, path_to_save_to + output_filename)
    return


def plot_username_vs_time(df,path_to_save_to: str,output_filename: str) -> None:
    """
    >>> output_filename = 'unique_user_names_per_day_'
    >>> path_to_save_to = "/home/appuser/app/static/"
    >>>
    """
    logger.info('[trace]')

    # https://stackoverflow.com/a/8228808/1164295
    plt.close('all')

    gb = df.groupby([(df['year']),(df['month']), (df['day'])]).nunique()['username'].plot(kind='bar')
    _=plt.ylabel('number of unique user names')
    _=plt.title('unique user name attempts observed per day')
    creation_date = datetime.datetime.now().strftime("%Y-%m-%d")

    plt.savefig(output_filename, format='png', bbox_inches = "tight")
    shutil.move(output_filename, path_to_save_to + output_filename)
    return

def plot_country_per_day_vs_time(df,path_to_save_to: str,output_filename: str) -> None:
    """
    >>> output_filename = 'unique_IP_address_per_country_above_threshold_per_day_'
    >>> path_to_save_to = "/home/appuser/app/static/"
    >>>
    """
    logger.info('[trace]')

    # https://stackoverflow.com/a/8228808/1164295
    plt.close('all')

    # https://stackoverflow.com/questions/26683654/making-a-stacked-barchart-in-pandas
    # https://stackoverflow.com/questions/34917727/stacked-bar-plot-by-grouped-data-with-pandas
    gb = df.groupby([(df['year']),(df['month']), (df['day']), (df['country'])])['ip'].nunique()
    gb_reduced = gb[gb>4]
    # https://stackoverflow.com/questions/4700614/how-to-put-the-legend-out-of-the-plot/43439132#43439132
    gb_reduced.unstack(level=-1).plot(kind='bar', stacked=True)
    _=plt.legend(bbox_to_anchor=(1.04,1), loc="upper left")
    _=plt.ylabel('unique IP addresses per country')
    _=plt.title('IP address per country observed per day where count>4')

    plt.savefig(output_filename, format='png', bbox_inches = "tight")
    shutil.move(output_filename, path_to_save_to + output_filename)
    return

# EOF
