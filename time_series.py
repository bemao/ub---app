# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 09:19:17 2016

"""

import pandas as pd
import datetime
import matplotlib.pyplot as plt
import seaborn as sns

in_path = '/desktop/datasets/logins.json'

df = pd.read_json(in_path)

def time_since(date):
    beg_date = datetime.datetime.strptime('1970-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    
    time_dif = date - beg_date
    
    return time_dif.total_seconds()

#time_since is the time (in seconds) that has passed since 1970-01-01 00:00:00
df['time_since'] = df.apply(lambda x: time_since(x['login_time']), axis = 1)

#creates 15-minute (900 second) buckets
df['time_since'].describe()   #min = 72736 (1970-01-01 20:12:16), 
                              #max = 8881058 (1970-04-13 18:57:38)
#need x buckets, starting at 72000 (1970-01-01 20:00:00), 
                 #ending at 8881200 (1970-04-13 19:00:00)

df['time_slot'] = pd.cut(df['time_since'], range(72000, 8882100, 900), labels = range(72900, 8882100, 900))
time_cts = pd.DataFrame(df.groupby(['time_slot'])['login_time'].count())
time_cts.reset_index(inplace=True)
time_cts.columns = ['time_slot', 'Counts']

#ensures there are no missing time_slots
time_line = pd.DataFrame(index = range(72000,8882100,900), data = [0]*9789, columns = ['time'])

time_out = time_line.merge(time_cts, how='left', left_index=True, right_on='time_slot')
time_out['cts'] = time_out.apply(lambda x: x['time']+x['Counts'], axis = 1)
time_out.sort_values(by = 'time_slot', inplace=True)

time_key = time_out.merge(df, how='left', left_on='time_slot', right_on='time_slot')

fig, ax = plt.subplots(4,1)
fig.set_size_inches(17,15)
fig.suptitle('All Logins: Jan 1 1970 - April 13 1970 ', fontsize=20)
for i in range(4):
    ax[i].set_ylim(0,80)
    ax[i].set_xticks([0]+range(64,2688,96))
    ax[i].set_xticklabels(['']+['Fr','Sa','Su','Mo','Tu','We','Th']*7)
ax[0].set_title("20:00 Jan 1 - 19:45 Jan 29")
ax[1].set_title("20:00 Jan 29 - 19:45 Feb 26")
ax[2].set_title("20:00 Feb 26 - 19:45 Mar 25")
ax[3].set_title("19:45 Mar 25 - 19:00 Apr 13")
fig = sns.tsplot(data=time_out['cts'][:2688], ax = ax[0]) #first 4 weeks
fig = sns.tsplot(data=time_out['cts'][2688:5376], ax = ax[1]) #second 4 weeks
fig = sns.tsplot(data=time_out['cts'][5376:8064], ax = ax[2]) #third 4 weeks
fig = sns.tsplot(data=time_out['cts'][8064:].tolist()+[-1.]*963, ax=ax[3])
for i in range(4):
    ax[i].vlines(672, ymin=0, ymax = 80, color = 'r')
    ax[i].vlines(1344, ymin=0, ymax = 80, color = 'r')
    ax[i].vlines(2016, ymin=0, ymax = 80, color = 'r')
fig_out = fig.get_figure()
fig_out.savefig('/desktop/overall.jpg', bbox_inches='tight')

fig, ax = plt.subplots(2,1)
fig.set_size_inches(15,13)
fig.suptitle("Logins: Special Days - 1970 ", fontsize=20)
for i in range(2):
    ax[i].set_ylim(0,80)
    ax[i].set_xticks(range(0,96, 4))
    ax[i].set_xticklabels([str(i)+":00" for i in xrange(0, 24)], rotation=45)
ax[0].set_title("St. Patrick's Day (Tuesday, March 17 1970)")
ax[1].set_title("Superbowl Sunday (Sunday, Jan 11 1970)")
fig = sns.tsplot(data=time_out['cts'][7121:7217], ax = ax[0])
fig = sns.tsplot(data=time_out['cts'][880:977], ax = ax[1])

fig_out = fig.get_figure()
fig_out.savefig('/desktop/special_days.jpg', bbox_inches='tight')


fig, ax = plt.subplots()
fig.set_size_inches(15,13)
fig.suptitle("Weekend Data: 5pm Friday - 5pm Sunday", fontsize =20)
ax.set_ylim(0,80)
ax.set_xticks(range(0,192,4))
for k in range(2):
    ax.vlines(29+96*k, ymin=0, ymax=80, color='r')
ax.text(8, 75, "Friday", fontsize=18)
ax.text(70, 75, "Saturday", fontsize=18)
ax.text(155, 75, "Sunday", fontsize=18)
ax.set_xticklabels(['']+[str(i)+":00" if i%2 == 0 else " " for i in xrange(18, 24)] + 
                    [str(i)+":00" if i%2 == 0 else " " for i in xrange(0, 24)]+ 
                    [str(i)+":00" if i%2 == 0 else " " for i in xrange(0, 18)], rotation=45)
i = 85
while i < len(time_out):
    fig = sns.tsplot(data=time_out['cts'][i:i+192], ax = ax)
    i+=672
    
fig_out = fig.get_figure()
fig_out.savefig('/desktop/weekends.jpg', bbox_inches='tight')


fig, ax = plt.subplots()
fig.set_size_inches(15,13)
fig.suptitle("Weekday Data: 5pm Sunday - 5pm Friday", fontsize =20)
ax.set_ylim(0,80)
ax.set_xticks(range(0,480, 4))
for k in range(5):
    ax.vlines(29+96*k, ymin=0, ymax=80, color='r')
ax.text(60, 75, "Monday", fontsize = 18)
ax.text(156, 75, "Tuesday", fontsize = 18)
ax.text(245, 75, "Wednesday", fontsize = 18)
ax.text(348, 75, "Thursday", fontsize = 18)
ax.text(435, 75, "Friday", fontsize = 18)
ax.set_xticklabels(['']+[str(j)+":00" if j%4 == 0 else " " for j in xrange(18, 24)] + 
                    [str(j)+":00" if j%4 == 0 else " " for j in xrange(0, 24)]*4+ 
                    [str(j)+":00" if j%4 == 0 else " " for j in xrange(0, 18)], rotation=45)
i = 277
for k in range(14):
    fig = sns.tsplot(data=time_out['cts'][i:i+480], ax = ax)
    i+=672

fig_out = fig.get_figure()
fig_out.savefig('/desktop/weekdays.jpg', bbox_inches='tight')





