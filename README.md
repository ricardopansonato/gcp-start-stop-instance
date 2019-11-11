### GCP - Start/Stop script

Tools that start/shutdown GCP instances on your scheduler.

### Config

[Creating service accounts](https://cloud.google.com/iam/docs/creating-managing-service-accounts)   
[Creating service account keys](https://cloud.google.com/iam/docs/creating-managing-service-account-keys)

- Update a yaml file ./config/instances.yaml as below:

```
- <project-name-1>:
   key: <Full path for service account keys. Links above describe how you can create it>
   zones:
      <gcp-instance-zone>:
         <instance-1>:
            week_day: <Week days that instance will be in running, for instance: Mon,Tues,Wed>
            active_hours: <Hours that instance will be in running, we can work with different time ranges, for instance: 0-4,13-14>
```

- Here is an example of this file:

```
- project-1:
   key: ./config/key-1.json
   zones:
      us-central1-a:
         instance-1:
            week_day: Mon,Tues,Wed,Thu,Fri,Sat,Sun
            active_hours: 0-4,13-14
- project-2:
   key: ./config/key-2.json
   zones:
      us-central1-a:
         instance-1:
            week_day: Mon,Tues,Wed,Thu,Fri,Sat,Sun
            active_hours: 0-4,13-14
         instance-2:
            week_day: Mon,Tues,Wed,Fri,Sat,Sun
            active_hours: 0-4,18-24
```

### Usage

After update yaml, you can do below command:

```
pip install -r requirements.txt
start-stop-instance.py -w 1 -c ./config/instances.yaml
```

Add line below to cron:

```
*/30 * * * * root /path/to/file/start-stop-instance.py -w 1 -c ./config/instances.yaml
```
