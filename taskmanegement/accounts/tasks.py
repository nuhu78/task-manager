import logging

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_team_assignment_email(self, team_id, employee_id):
    """
    Send email notification to employee when assigned to a team by a manager.
    Runs in background via Celery so the API responds instantly.
    """
    from accounts.models import Team, User

    try:
        team = Team.objects.select_related('manager').get(id=team_id)
        employee = User.objects.get(id=employee_id)

        manager_name = team.manager.get_full_name() or team.manager.username
        employee_name = employee.get_full_name() or employee.username

        subject = f'You have been added to team "{team.name}"'
        message = (
            f'Hello {employee_name},\n\n'
            f'You have been added to a new team.\n\n'
            f'Team: {team.name}\n'
            f'Manager: {manager_name}\n'
        )

        if team.description:
            message += f'Description: {team.description}\n'

        message += (
            f'\nPlease reach out to your manager if you have any questions.\n\n'
            f'Regards,\n'
            f'Task Manager Team'
        )

        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@taskmanager.com')

        send_mail(
            subject,
            message,
            from_email,
            [employee.email],
            fail_silently=False,
        )

        logger.info(f'Team assignment email sent to {employee.email} for team "{team.name}"')
        return f'Email sent to {employee.email}'

    except Team.DoesNotExist:
        logger.error(f'Team {team_id} not found')
        return f'Team {team_id} not found'

    except User.DoesNotExist:
        logger.error(f'Employee {employee_id} not found')
        return f'Employee {employee_id} not found'

    except Exception as exc:
        logger.error(f'Failed to send email: {exc}')
        raise self.retry(exc=exc)
