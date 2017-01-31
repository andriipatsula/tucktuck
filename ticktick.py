# coding=utf-8
import re
import json
import urllib2
import cookielib


class TickProfile:
    def __init__(self):
        """
        Create an object of TickProfile.

        It represents the entire TicTick tasks/lists hierarchy.
        """
        self.tasks = dict()
        self.projects = dict()
        self.removed_tasks = list()

    def add_task(self, task_id, task):
        """
        """
        if task and task.project_id:
            project = self.projects.get(task.project_id)
            if project:
                project.add_task(task_id, task)
                task.set_project(project)

        self.tasks[task_id] = task

    def add_removed_task(self, task_id):
        """
        """
        self.removed_tasks.append(task_id)

    def add_project(self, project_id, project):
        """
        """
        self.projects[project_id] = project

    def clear(self):
        """
        """
        self.tasks.clear()
        self.projects.clear()
        del self.removed_tasks[:]

    def __str__(self):
        """
        Return string representation of TickProfile.
        """
        buffer = str()
        for project_id, project in self.projects.iteritems():
            buffer += '#{0}, {1}\n'.format(project_id, project.name)
            for task_id, task in project.tasks.iteritems():
                buffer += '\t{0} #{1}, {2}\n'.format('✔' if task.is_completed() else ' ', task_id, task.title)

        return buffer


class TickProject(object):
    def __init__(self):
        """
        """
        self.project_id = None
        self.name = None
        self.pictograms = None
        self.color = None
        self.tasks = dict()

    def add_task(self, task_id, task):
        """
        """
        self.tasks[task_id] = task

    @staticmethod
    def from_json(project):
        """
        """
        def __get_emoji_list(name):
            """
            Find all emoji symbols in project name.

            Dirty hack. todo: Find better solution for retrieving emoji symbols from title.
            """
            # return re.findall(emoji_codes, name, re.UNICODE)
            res = list()
            splitted = name.split(' ')
            if len(splitted) > 1 and len(splitted[0]) <= 4:
                res.append(splitted[0])
            return res


        tickproject = TickProject()

        tickproject.project_id = project.get('id')
        ## Can consist utf-8 symbols (like enoji).
        tickproject.name = project.get('name').encode('utf-8').strip()
        tickproject.color = project.get('color')
        emoji = __get_emoji_list(tickproject.name)
        if emoji:
            tickproject.pictograms = ''.join(emoji)

        return tickproject


class TickTask(object):
    class Status(object):
        """
        Status of the task.
        For subtask exists one more =1.
        """
        Closed = 2
        Opened = 0

    class Priority(object):
        """
        """
        Hight = 5
        Medium = 3
        Low = 1

    def __init__(self):
        """
        """
        self.task_id = None
        self.all_day = None
        self.project_id = None
        self.project = None
        self.title = None
        self.content = None
        self.due_date = None
        self.time_zone = None
        # self.reminder = None
        # self.repeat_first_date = None
        # self.repeat_flag = None
        self.completed_time = None
        self.repeate_task_id = None
        self.priority = None
        self.status = None
        self.created_time = None
        self.modified_time = None

    def set_project(self, project):
        self.project = project

    def is_completed(self):
        """
        Check if task is completed.
        """
        return True if self.completed_time is not None and self.status != TickTask.Status.Opened else False

    def has_due_date(self):
        """
        Check if task has dueDate set.
        Possible 2 values: None, date
        """
        return True if self.due_date is not None else False

    def is_all_day(self):
        """
        Check if task has isAllDay set.
        Possible 3 values: None, True, False
        """
        return True if self.all_day is not None and self.all_day else False

    def get_summary(self):
        """
        Get task's summary. Repersents state, priority and type.
        """
        summary = str()
        if self.is_completed() == True:
            summary += '✔️'
        if self.project.pictograms:
            summary += self.project.pictograms
        if self.priority:
            if self.priority == TickTask.Priority.Low:
                summary += '🔻'
            elif self.priority == TickTask.Priority.Hight:
                summary += '🔺'
            elif self.priority == TickTask.Priority.Medium:
                summary += '⚫️'

        if self.title:
            summary += self.title
        return summary

    def get_description(self):
        """
        """
        return self.content

    def get_color(self):
        """
        """
        return self.project.color

    @staticmethod
    def from_json(task):
        """
        """
        ticktask = TickTask()

        ticktask.task_id = task.get('id')
        ticktask.all_day = task.get('isAllDay')
        ticktask.project_id = task.get('projectId')
        ticktask.title = task.get('title').encode('utf-8').strip()
        if task.get('content'):
            ticktask.content = task.get('content').encode('utf-8').strip()
        else:
            ticktask.content = ''
        if task.get('desc'):
            ticktask.content += task.get('desc').encode('utf-8').strip()
        items = task.get('items')
        if items:
            for item in items:
                if item['status'] == 0:
                    ticktask.content += '\n◻️'
                else:
                    ticktask.content += '\n☑️'
                ticktask.content += item['title'].encode('utf-8').strip()
        ticktask.due_date = task.get('dueDate')
        ticktask.time_zone = task.get('timeZone')
        ticktask.completed_time = task.get('completedTime')
        ticktask.priority = task.get('priority')
        ticktask.status = task.get('status')
        ticktask.created_time = task.get('createdTime')
        ticktask.modified_time = task.get('modifiedTime')
        ticktask.repeate_task_id = task.get('repeatTaskId')

        return ticktask


class TickTick:
    def __init__(self, username, password):
        """
        """
        self.opener = None
        self.username = username
        self.password = password

        self.profile = TickProfile()

    def signon(self):
        """
        """
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))

        params = {'username' : self.username, 'password' : self.password}
        params = json.dumps(params)

        headers = {'Content-Type': 'application/json', 'Connection' : 'keep-alive'}

        url = 'https://ticktick.com/api/v2/user/signon?wc=true&remember=true'
        self.__open_url(url, params, headers)

    def sign_out(self):
        """
        """
        url = 'https://ticktick.com/api/v2/user/signout'
        self.__open_url(url)

    def fetch_profile(self, point = 1000000):
        """
        """
        url = 'https://ticktick.com/api/v2/batch/check/{0}'.format(point)
        responce = self.__open_url(url)

        profile = json.loads(responce.read())
        tasks = profile.get('syncTaskBean')
        projects = profile.get('projectProfiles')

        self.profile.clear()

        inbox_id = profile.get('inboxId')
        if inbox_id:
            project = TickProject()
            project.project_id = inbox_id
            project.name = 'Inbox'
            self.profile.add_project(inbox_id, project)

        if projects:
            for project in projects:
                project = TickProject.from_json(project)
                self.profile.add_project(project.project_id, project)

        if tasks:
            updates = tasks.get('update')
            if updates:
                for task in updates:
                    task = TickTask.from_json(task)
                    self.profile.add_task(task.task_id, task)

            removes = tasks.get('delete')
            if removes:
                for task in removes:
                    self.profile.add_removed_task(task['taskId'])


    def close_connection(self):
        """
        """
        if self.opener:
            self.opener.close()

    def __open_url(self, url, params=None, headers={}):
        """
        """
        request = urllib2.Request(url, params, headers)
        try:
            if self.opener:
                return self.opener.open(request)
            else:
                raise Exception('Connection is not established')
        except Exception:
            raise
