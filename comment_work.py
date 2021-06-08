
import requests
from .settings import API_USER, API_TOKEN, SOURCE_LINK, TARGET_PROJECT


def get_project_issues(project_id):
    """
    :param project_id
    :return: list of issue_id
    """
    # используем jql для получения всех issue, так как там и лежат комменты
    link = SOURCE_LINK + 'search?jql=project=' + "'" + project_id + "'"
    data = requests.get(link, auth=(API_USER, API_TOKEN)).json()
    # в data получаем выдачу с ключом issues - где в списке все они перечисленны
    issues_list = data['issues']
    issues_id_list = []
    for issue in issues_list:
        issues_id_list.append(issue['id'])
    return issues_id_list


def get_commentaries_from_issue(issue_id):
    """"
    тут получаем комментарии из issue и выдаем их в dict ()
    """
    link = SOURCE_LINK + 'issue/' + issue_id
    data = requests.get(link, auth=(API_USER, API_TOKEN)).json()
    comments_list = data['fields']['comment']['comments']  # получили список всех комментов из issue
    # переведем в  вид: id коммента (надо для дальнейшего удаления?), автор, datetime, сам коммент
    list_of_comment_data = []
    for comment in comments_list:
        body_text = ''
        for content in comment['body']['content']:
            for content_piece in content['content']:
                try:
                    body_text += content_piece['text']
                except KeyError:
                    pass

        organized_comment_data = {
            'id': comment['id'],
            'issueId': issue_id,
            'author': comment['author']['accountId'],
            'datetime': comment['created'],
            'body': body_text
        }
        list_of_comment_data.append(organized_comment_data)
    return list_of_comment_data


def delete_commentaries(comment_data_list):
    """
    :param comment_data_list: список комментариев
    :return:
    """
    print(comment_data_list)
    if comment_data_list:
        for comment in comment_data_list:
            link = SOURCE_LINK + 'issue/' + comment[0]['issueId'] + '/comment/' + comment[0]['id']
            requests.delete(link, auth=(API_USER, API_TOKEN))
    return 0


def post_result(comment_list):
    """
    :param comment_list: список комментов, видимо, полная инфа и тело и данные
    :return: айди коммента под проектом
    """
    result_text = ''
    issue_id = ''
    for comment in comment_list:
        issue_id = comment['issueId']
        line = "\n\n" + comment['author'] + " commented at " + comment['datetime'] + ": \n\'" + comment['body'] + "\'"
        result_text += line
    link = SOURCE_LINK + 'issue/' + issue_id + '/comment/'
    body_of_comment_request = {
        'type': 'doc',
        'version': '1',
        'content':
            {
                'type': 'paragraph',
                'content': [
                    {
                        'text': result_text,
                        'type': 'text'
                    }
                ]
            }
    }
    post_request = requests.post(link, auth=(API_USER, API_TOKEN), data=body_of_comment_request)


def commentary_work_on_project(project_id):
    # собираем данные о комментариях в проекте и публикуем их на соответствующих задачах в заданном формате
    issues_id_list = get_project_issues(project_id)
    commentary_organized_data = []
    for issue_id in issues_id_list:
        commentary_organized_data.append(get_commentaries_from_issue(issue_id))
    for comment_list in commentary_organized_data:
        post_result(comment_list)
    for comment_list in commentary_organized_data:
        for comment in comment_list:
            delete_commentaries(comment)


commentary_work_on_project(TARGET_PROJECT)

