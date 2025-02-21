from dataclasses import dataclass

from pprint import pprint

import aiohttp
import datetime as dt
import json

from Library.utils.DictDot import DictDot
from ..utils.DictDot import DictDot
from .DomoAuth import DomoFullAuth
from enum import Enum
from .routes import job_routes

class WatchDogType(Enum):
    DATASET_ERRORS = 'error_detection'
    DATASET_INDEX_TIME = 'max_indexing_time'
    LAST_UPDATED_DATA = 'last_data_updated'
    ROW_COUNT_CHANGE = 'row_count_variance'
    CUSTOM_QUERY = 'custom_query'
    OUTLIER_EXECUTION = 'execution_variance'

    
@dataclass
class DomoTrigger_Schedule:
    schedule_text: str = None
    schedule_type: str = 'scheduleTriggered'

    minute: int = None
    hour: int = None
    minute_str: str = None
    hour_str : str = None
        
    @classmethod
    def _from_str(cls, s_text, s_type):
        sched = cls(
            schedule_type=s_type,
            schedule_text=s_text)

        try:
            parsed_hour =s_text.split(' ')[2]
            parsed_minute=s_text.split(' ')[1]
            
            if "*" in parsed_hour or "/" in parsed_hour:
                sched.hour_str = parsed_hour
            else:
                sched.hour = int(float(parsed_hour))
            if "*" in parsed_minute:
                sched.minute_str = parsed_minute
            else:
                sched.minute = int(float(parsed_minute))

            return sched

        except Exception as e:
            print(f"unable to parse schedule {s_text}")
            print(e)

    def to_obj(self):
        return {'hour': int(self.hour),
                'minute': int(self.minute)}

    def to_schedule_obj(self):
        minute = self.minute_str if self.minute_str is not None else str(self.minute)
        hour = self.hour_str if self.hour_str is not None else str(self.hour)
        return {
            "eventEntity": f'0 {minute} {hour} ? * *',
            #old value on Jan 13
            #"eventEntity": f'0 {minute} {hour} 1/1 * ? *',
            "eventType": self.schedule_type
        }


@dataclass
class DomoTrigger:
    id: str
    job_id: str
    schedule: [DomoTrigger_Schedule] = None


@dataclass
class DomoJob:
    id: str
    name: str
    description :str
    remote_instance: str
    user_id: str
    application_id: str
    customer_id: str
    execution_timeout: int
    entity_ids: list
    job_type: str
    entity_type: str
    max_indexing_time_min :int
    variance_percent: int
    min_update_frequency_min: int
    sql_query:str
    notify_user_ids: list
    metrics_dataset_id: str
    notify_group_ids: list
    notify_email_addressess: list
    resources_requests: str
    resources_limits: str
    
    triggers: [DomoTrigger] = None

    @classmethod
    def _from_json(cls, obj):
        dd = DictDot(obj)
        triggers_ls = obj.get('triggers', None)

        triggers_dj = [DomoTrigger(
            id=tg.get('triggerId'),
            job_id=tg.get('jobId'),

            schedule=DomoTrigger_Schedule._from_str(
                s_text=tg.get('eventEntity'),
                s_type=tg.get('eventType'))
        ) for tg in triggers_ls]

        return cls(id=dd.jobId,
                   application_id=dd.applicationId,
                   customer_id=dd.customerId,
                   name=dd.jobName,
                   description = dd.jobDescription,
                   user_id=dd.userId,
                   remote_instance=dd.executionPayload.remoteInstance.replace(
                       '.domo.com', '') if dd.executionPayload.remoteInstance else None,
                   execution_timeout = dd.executionTimeout,
                   entity_ids = dd.executionPayload.watcherParameters.entityIds if dd.executionPayload.watcherParameters else [],
                   job_type = dd.executionPayload.watcherParameters.type if dd.executionPayload.watcherParameters else [],
                   entity_type=dd.executionPayload.watcherParameters.entityType if dd.executionPayload.watcherParameters else [],
                   max_indexing_time_min = dd.executionPayload.watcherParameters.maxIndexingTimeInMinutes if dd.executionPayload.watcherParameters else [],
                   variance_percent = dd.executionPayload.watcherParameters.variancePercent if dd.executionPayload.watcherParameters else [],
                   min_update_frequency_min = dd.executionPayload.watcherParameters.minDataUpdateFrequencyInMinutes if dd.executionPayload.watcherParameters else [],
                   sql_query=dd.executionPayload.watcherParameters.sqlQuery if dd.executionPayload.watcherParameters else [],
                   notify_user_ids=dd.executionPayload.notifyUserIds,
                   metrics_dataset_id=dd.executionPayload.metricsDatasetId,
                   notify_group_ids=dd.executionPayload.notifyGroupIds,
                   notify_email_addressess=dd.executionPayload.notifyEmailAddresses,
                   resources_requests =dd.resources.requests.memory,
                   resources_limits = dd.resources.limits.memory,
                   triggers=triggers_dj)
    def get_body (self):
        body = {
        "jobName": self.name,
        "jobDescription": self.description,
        "executionTimeout": self.execution_timeout,
        "accounts": [],
        "executionPayload": {
            "notifyUserIds": self.notify_user_ids or [],
            "notifyGroupIds": self.notify_group_ids or [],
            "notifyEmailAddresses": self.notify_email_addressess or [],
        "watcherParameters": {
          "entityIds": self.entity_ids,
          "type": self.job_type,
          "entityType": self.entity_type,
          "maxIndexingTimeInMinutes":self.max_indexing_time_min,
          "variancePercent": self.variance_percent,
          "sqlQuery": self.sql_query
            },
        "metricsDatasetId": self.metrics_dataset_id
          },
        "resources": {
            "requests": {"memory": self.resources_requests},
            "limits": {"memory": self.resources_limits}
        },
        "triggers": [self.triggers[0].schedule.to_schedule_obj()] if len(self.triggers)>0 else []
        }
        return body

        
    @classmethod
    async def create_domostats_job(cls,
                                   full_auth: DomoFullAuth,
                                   domostats_schedule: DomoTrigger_Schedule,
                                   application_id: str,
                                   target_instance: str,
                                   report_dict: dict,
                                   output_dataset_id: str,
                                   account_id: str,
                                   execution_timeout: int = 1440,
                                   debug: bool = False, log_results: bool = False,
                                   session: aiohttp.ClientSession = None):

        schedule_obj = domostats_schedule.to_schedule_obj()

        body = job_routes.generate_body_remote_domostats(target_instance=target_instance,
                                                         report_dict=report_dict,
                                                         output_dataset_id=output_dataset_id,
                                                         account_id=account_id,
                                                         schedule_ls=[
                                                             schedule_obj],
                                                         execution_timeout=execution_timeout)
        
        res = await job_routes.add_job(full_auth=full_auth,
                                       application_id=application_id,
                                       body=body,
                                       debug=debug,
                                       log_results=log_results,
                                       session=session)
        if debug:
            print(res)

        if res.status != 200:
            return False

        return True

    @classmethod
    async def create_watchdog_job(cls,
                                   full_auth: DomoFullAuth,
                                   body : str,
                                    application_id : str,
                                   debug: bool = False, log_results: bool = False,
                                   session: aiohttp.ClientSession = None):
            
            
        res = await job_routes.add_job(full_auth=full_auth,
                                       application_id=application_id,
                                       body=body,
                                       debug=debug,
                                       log_results=log_results,
                                       session=session)

#         if debug:
#             print(res)

        if res.status != 200:
            return False

        return True
    
    @classmethod
    async def generate_watchdog_body(cls,
                                   watchdog_report_type : WatchDogType,
                                   watchdog_schedule: DomoTrigger_Schedule,
                                   job_name: str,
                                   notify_user_ids_ls: list,
                                   notify_group_ids_ls: list,
                                   notify_emails_ls: list,
                                   entity_ids_ls: list,
                                   entity_type : str,
                                   metric_dataset_id: str,
                                   sql_query :str = None,
                                   variance_percent: int = 30,
                                   max_indexing_time_mins: int = 30,
                                   execution_timeout: int = 1440,
                                   min_update_frequency_min: int = 1440,
                           ):
        schedule_obj = watchdog_schedule.to_schedule_obj()

        body = job_routes.generate_body_watchdog_generic(job_name=job_name,
                                                         notify_user_ids_ls=notify_user_ids_ls,
                                                         notify_group_ids_ls=notify_group_ids_ls,
                                                         notify_emails_ls=notify_emails_ls,
                                                         entity_ids_ls = entity_ids_ls,
                                                         entity_type=entity_type,
                                                         metric_dataset_id=metric_dataset_id,
                                                         schedule_ls=[
                                                             schedule_obj],
                                                         job_type = watchdog_report_type.value,
                                                         execution_timeout=execution_timeout)
        

        
        if watchdog_report_type == watchdog_report_type.DATASET_INDEX_TIME:
            child ={ "maxIndexingTimeInMinutes": max_indexing_time_mins }
            body["executionPayload"]["watcherParameters"].update(child)

  
        
        if watchdog_report_type == watchdog_report_type.ROW_COUNT_CHANGE or watchdog_report_type == watchdog_report_type.OUTLIER_EXECUTION:
            child ={ "variancePercent": variance_percent }
            body["executionPayload"]["watcherParameters"].update(child)
            
        
        if watchdog_report_type == watchdog_report_type.CUSTOM_QUERY:
            child ={ "sqlQuery": sql_query }
            body["executionPayload"]["watcherParameters"].update(child)
            
        if watchdog_report_type == watchdog_report_type.LAST_UPDATED_DATA:
            child ={ "minDataUpdateFrequencyInMinutes": min_update_frequency_min }
            body["executionPayload"]["watcherParameters"].update(child)
            
            
        return body
                            
                            
                            
    @classmethod
    async def update_job(cls,
                         full_auth: DomoFullAuth,
                         body: str,
                         job_id: str,
                         application_id: str,
                         debug: bool = False,
                         log_results: bool = False,
                        session: aiohttp.ClientSession = None):
        

        res = await job_routes.update_job(full_auth=full_auth,
                                          body=body,
                                       application_id=application_id,
                                       job_id = job_id,
                                       debug=debug,
                                       log_results=log_results,
                                       session=session)


        if res.status != 200:
            return False

        return True
                         