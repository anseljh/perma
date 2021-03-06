from django.core.urlresolvers import reverse

from perma.models import *

from .utils import PermaTestCase


class UserManagementViewsTestCase(PermaTestCase):

    fixtures = ['fixtures/users.json',
                'fixtures/folders.json',
                'fixtures/archive.json',
                ]

    def setUp(self):
        super(UserManagementViewsTestCase, self).setUp()

        self.admin_user = LinkUser.objects.get(pk=1)
        self.registrar_user = LinkUser.objects.get(pk=2)
        self.regular_user = LinkUser.objects.get(pk=4)
        self.registrar = self.registrar_user.registrar
        self.pending_registrar = Registrar.objects.get(pk=2)
        self.unrelated_registrar = Registrar.objects.exclude(pk=self.registrar.pk).first()
        self.unrelated_registrar_user = self.unrelated_registrar.users.first()
        self.organization = Organization.objects.get(pk=1)
        self.organization_user = self.organization.users.first()
        self.another_organization = Organization.objects.get(pk=2)
        self.unrelated_organization = self.unrelated_registrar.organizations.first()
        self.unrelated_organization_user = self.unrelated_organization.users.first()
        self.deletable_organization = Organization.objects.get(pk=3)

    ### REGISTRAR A/E/D VIEWS ###

    def test_registrar_list_filters(self):
        # get just approved registrars
        self.get('user_management_manage_registrar',
                 user=self.admin_user,
                 request_kwargs={'data':{'status':'approved'}})

        # get just pending registrars
        self.get('user_management_manage_registrar',
                 user=self.admin_user,
                 request_kwargs={'data': {'status': 'pending'}})

    def test_admin_can_create_registrar(self):
        self.submit_form(
            'user_management_manage_registrar', {
                'a-name':'test_views_registrar',
                'a-email':'test@test.com',
                'a-website':'http://test.com'
            },
            user=self.admin_user,
            success_url=reverse('user_management_manage_registrar'),
            success_query=Registrar.objects.filter(name='test_views_registrar'))

    def test_admin_can_update_registrar(self):
        self.submit_form('user_management_manage_single_registrar',
                         user=self.admin_user,
                         reverse_kwargs={'args':[self.unrelated_registrar.pk]},
                         data={
                              'a-name': 'new_name',
                              'a-email': 'test@test.com2',
                              'a-website': 'http://test.com'},
                         success_url=reverse('user_management_manage_registrar'),
                         success_query=Registrar.objects.filter(name='new_name'))

    def test_registrar_can_update_registrar(self):
        self.submit_form('user_management_manage_single_registrar',
                         user=self.registrar_user,
                         reverse_kwargs={'args': [self.registrar.pk]},
                         data={
                             'a-name': 'new_name',
                             'a-email': 'test@test.com2',
                             'a-website': 'http://test.com'},
                         success_url=reverse('user_management_settings_organizations'),
                         success_query=Registrar.objects.filter(name='new_name'))

    def test_registrar_cannot_update_unrelated_registrar(self):
        self.get('user_management_manage_single_registrar',
                 user=self.registrar_user,
                 reverse_kwargs={'args': [self.unrelated_registrar.pk]},
                 require_status_code=404)

    def test_admin_can_approve_pending_registrar(self):
        self.submit_form('user_management_approve_pending_registrar',
                         user=self.admin_user,
                         data={'status':'approved'},
                         reverse_kwargs={'args': [self.pending_registrar.pk]},
                         success_query=Registrar.objects.filter(pk=self.pending_registrar.pk,
                                                                status="approved").exists())

    def test_admin_can_deny_pending_registrar(self):
        self.submit_form('user_management_approve_pending_registrar',
                         user=self.admin_user,
                         data={'status': 'denied'},
                         reverse_kwargs={'args': [self.pending_registrar.pk]},
                         success_query=Registrar.objects.filter(pk=self.pending_registrar.pk,
                                                                status="denied").exists())

    ### ORGANIZATION A/E/D VIEWS ###

    def test_organization_list_filters(self):
        # get orgs for a single registrar
        self.get('user_management_manage_organization',
                 user=self.admin_user,
                 request_kwargs={'data': {'registrar': self.registrar.pk}})

    def test_admin_can_create_organization(self):
        self.submit_form('user_management_manage_organization',
                         user=self.admin_user,
                         data={
                             'a-name': 'new_name',
                             'a-registrar': self.registrar.pk},
                         success_url=reverse('user_management_manage_organization'),
                         success_query=Organization.objects.filter(name='new_name'))

    def test_registrar_can_create_organization(self):
        self.submit_form('user_management_manage_organization',
                         user=self.registrar_user,
                         data={
                             'a-name': 'new_name'},
                         success_url=reverse('user_management_manage_organization'),
                         success_query=Organization.objects.filter(name='new_name'))

    def test_admin_can_update_organization(self):
        self.submit_form('user_management_manage_single_organization',
                         user=self.admin_user,
                         reverse_kwargs={'args':[self.organization.pk]},
                         data={
                             'a-name': 'new_name',
                             'a-registrar': self.registrar.pk},
                         success_url=reverse('user_management_manage_organization'),
                         success_query=Organization.objects.filter(name='new_name'))

    def test_registrar_can_update_organization(self):
        self.submit_form('user_management_manage_single_organization',
                         user=self.registrar_user,
                         reverse_kwargs={'args':[self.organization.pk]},
                         data={
                             'a-name': 'new_name'},
                         success_url=reverse('user_management_manage_organization'),
                         success_query=Organization.objects.filter(name='new_name'))

    def test_org_user_can_update_organization(self):
        self.submit_form('user_management_manage_single_organization',
                         user=self.organization_user,
                         reverse_kwargs={'args': [self.organization.pk]},
                         data={
                             'a-name': 'new_name'},
                         success_url=reverse('user_management_manage_organization'),
                         success_query=Organization.objects.filter(name='new_name'))

    def test_registrar_cannot_update_unrelated_organization(self):
        self.get('user_management_manage_single_organization',
                 user=self.registrar_user,
                 reverse_kwargs={'args': [self.unrelated_organization.pk]},
                 require_status_code=404)

    def test_org_user_cannot_update_unrelated_organization(self):
        self.get('user_management_manage_single_organization',
                 user=self.organization_user,
                 reverse_kwargs={'args': [self.unrelated_organization.pk]},
                 require_status_code=404)

    def _delete_organization(self, user):
        self.submit_form('user_management_manage_single_organization_delete',
                         user=user,
                         reverse_kwargs={'args': [self.deletable_organization.pk]},
                         success_url=reverse('user_management_manage_organization'),
                         success_query=Organization.objects.filter(user_deleted=True, pk=self.deletable_organization.pk))

    def test_admin_user_can_delete_empty_organization(self):
        self._delete_organization(self.admin_user)

    def test_registrar_user_can_delete_empty_organization(self):
        self._delete_organization(self.deletable_organization.registrar.users.first())

    def test_org_user_can_delete_empty_organization(self):
        self._delete_organization(self.deletable_organization.users.first())

    def test_cannot_delete_nonempty_organization(self):
        self.submit_form('user_management_manage_single_organization_delete',
                         user=self.admin_user,
                         reverse_kwargs={'args': [self.organization.pk]},
                         require_status_code=404)

    ### USER A/E/D VIEWS ###

    def test_create_and_delete_user(self):
        self.log_in_user(self.admin_user)

        base_user = {
            'a-first_name':'First',
            'a-last_name':'Last',
        }
        email = 'test_views_test@test.com'

        for view_name, form_extras in [
            ['registrar_user', {'a-registrar': 1}],
            ['user', {}],
            ['organization_user', {'a-organizations': 1}],
        ]:
            # create user
            email += '1'
            self.submit_form('user_management_' + view_name + '_add_user',
                           data=dict(base_user.items() + form_extras.items() + [['a-email', email]]),
                           success_url=reverse('user_management_manage_' + view_name),
                           success_query=LinkUser.objects.filter(email=email))
            new_user = LinkUser.objects.get(email=email)

            # delete user (deactivate)
            new_user.is_confirmed = True
            new_user.save()
            self.submit_form('user_management_manage_single_' + view_name + '_delete',
                           reverse_kwargs={'args': [new_user.pk]},
                           success_url=reverse('user_management_manage_' + view_name))

            # reactivate user
            self.submit_form('user_management_manage_single_' + view_name + '_reactivate',
                           reverse_kwargs={'args': [new_user.pk]},
                           success_url=reverse('user_management_manage_' + view_name))

            # delete user (really delete)
            new_user.is_confirmed = False
            new_user.save()
            self.submit_form('user_management_manage_single_' + view_name + '_delete',
                           reverse_kwargs={'args': [new_user.pk]},
                           success_url=reverse('user_management_manage_' + view_name))

    ### ADDING NEW USERS TO ORGANIZATIONS ###

    def test_admin_user_can_add_new_user_to_org(self):
        self.log_in_user(self.admin_user)
        self.submit_form('user_management_organization_user_add_user',
                         data={'a-organizations': self.organization.pk,
                               'a-first_name': 'First',
                               'a-last_name': 'Last',
                               'a-email': 'doesnotexist@example.com'},
                         query_params={'email': 'doesnotexist@example.com'},
                         success_url=reverse('user_management_manage_organization_user'),
                         success_query=LinkUser.objects.filter(email='doesnotexist@example.com',
                                                               organizations=self.organization).exists())


    def test_registrar_user_can_add_new_user_to_org(self):
        self.log_in_user(self.registrar_user)
        self.submit_form('user_management_organization_user_add_user',
                         data={'a-organizations': self.organization.pk,
                               'a-first_name': 'First',
                               'a-last_name': 'Last',
                               'a-email': 'doesnotexist@example.com'},
                         query_params={'email': 'doesnotexist@example.com'},
                         success_url=reverse('user_management_manage_organization_user'),
                         success_query=LinkUser.objects.filter(email='doesnotexist@example.com',
                                                               organizations=self.organization).exists())


    def test_org_user_can_add_new_user_to_org(self):
        self.log_in_user(self.organization_user)
        self.submit_form('user_management_organization_user_add_user',
                         data={'a-organizations': self.organization.pk,
                               'a-first_name': 'First',
                               'a-last_name': 'Last',
                               'a-email': 'doesnotexist@example.com'},
                         query_params={'email': 'doesnotexist@example.com'},
                         success_url=reverse('user_management_manage_organization_user'),
                         success_query=LinkUser.objects.filter(email='doesnotexist@example.com',
                                                               organizations=self.organization).exists())

    def test_registrar_user_cannot_add_new_user_to_inaccessible_org(self):
        self.log_in_user(self.registrar_user)
        self.submit_form('user_management_organization_user_add_user',
                         data={'a-organizations': self.unrelated_organization.pk,
                               'a-first_name': 'First',
                               'a-last_name': 'Last',
                               'a-email': 'doesnotexist@example.com'},
                         query_params={'email': 'doesnotexist@example.com'},
                         error_keys=['organizations'])
        self.assertFalse(LinkUser.objects.filter(email='doesnotexist@example.com',
                                                 organizations=self.unrelated_organization).exists())

    def test_org_user_cannot_add_new_user_to_inaccessible_org(self):
        self.log_in_user(self.organization_user)
        self.submit_form('user_management_organization_user_add_user',
                         data={'a-organizations': self.unrelated_organization.pk,
                               'a-first_name': 'First',
                               'a-last_name': 'Last',
                               'a-email': 'doesnotexist@example.com'},
                         query_params={'email': 'doesnotexist@example.com'},
                         error_keys=['organizations'])
        self.assertFalse(LinkUser.objects.filter(email='doesnotexist@example.com',
                                                 organizations=self.unrelated_organization).exists())

    ### ADDING EXISTING USERS TO ORGANIZATIONS ###

    def test_admin_user_can_add_existing_user_to_org(self):
        self.log_in_user(self.admin_user)
        self.submit_form('user_management_organization_user_add_user',
                         data={'a-organizations': self.organization.pk},
                         query_params={'email': self.regular_user.email},
                         success_url=reverse('user_management_manage_organization_user'),
                         success_query=self.regular_user.organizations.filter(pk=self.organization.pk))

    def test_registrar_user_can_add_existing_user_to_org(self):
        self.log_in_user(self.registrar_user)
        self.submit_form('user_management_organization_user_add_user',
                         data={'a-organizations': self.organization.pk},
                         query_params={'email': self.regular_user.email},
                         success_url=reverse('user_management_manage_organization_user'),
                         success_query=self.regular_user.organizations.filter(pk=self.organization.pk))

    def test_org_user_can_add_existing_user_to_org(self):
        self.log_in_user(self.organization_user)
        self.submit_form('user_management_organization_user_add_user',
                         data={'a-organizations': self.organization.pk},
                         query_params={'email': self.regular_user.email},
                         success_url=reverse('user_management_manage_organization_user'),
                         success_query=self.regular_user.organizations.filter(pk=self.organization.pk))

    def test_registrar_user_cannot_add_existing_user_to_inaccessible_org(self):
        self.log_in_user(self.registrar_user)
        self.submit_form('user_management_organization_user_add_user',
                         data={'a-organizations': self.unrelated_organization.pk},
                         query_params={'email': self.regular_user.email},
                         error_keys=['organizations'])
        self.assertFalse(self.regular_user.organizations.filter(pk=self.unrelated_organization.pk).exists())

    def test_org_user_cannot_add_existing_user_to_inaccessible_org(self):
        self.log_in_user(self.organization_user)
        self.submit_form('user_management_organization_user_add_user',
                         data={'a-organizations': self.another_organization.pk},
                         query_params={'email': self.regular_user.email},
                         error_keys=['organizations'])
        self.assertFalse(self.regular_user.organizations.filter(pk=self.another_organization.pk).exists())

    def test_cannot_add_admin_user_to_org(self):
        self.log_in_user(self.organization_user)
        resp = self.submit_form('user_management_organization_user_add_user',
                         data={'a-organizations': self.organization.pk},
                         query_params={'email': self.admin_user.email})
        self.assertIn("is an admin user", resp.content)
        self.assertFalse(self.admin_user.organizations.exists())

    def test_cannot_add_registrar_user_to_org(self):
        self.log_in_user(self.organization_user)
        resp = self.submit_form('user_management_organization_user_add_user',
                                data={'a-organizations': self.organization.pk},
                                query_params={'email': self.registrar_user.email})
        self.assertIn("is already a registrar user", resp.content)
        self.assertFalse(self.registrar_user.organizations.exists())

    ### REMOVING USERS FROM ORGANIZATIONS ###

    def test_can_remove_user_from_organization(self):
        self.log_in_user(self.registrar_user)
        self.submit_form('user_management_manage_single_organization_user_remove',
                         data={'org': self.organization.pk},
                         reverse_kwargs={'args': [self.organization_user.pk]},
                         success_url=reverse('user_management_manage_organization_user'))
        self.assertFalse(self.organization_user.organizations.filter(pk=self.organization.pk).exists())

    def test_registrar_cannot_remove_unrelated_user_from_organization(self):
        self.log_in_user(self.registrar_user)
        self.submit_form('user_management_manage_single_organization_user_remove',
                         data={'org': self.unrelated_organization.pk},
                         reverse_kwargs={'args': [self.unrelated_organization_user.pk]},
                         require_status_code=404)

    def test_org_user_cannot_remove_unrelated_user_from_organization(self):
        self.log_in_user(self.organization_user)
        self.submit_form('user_management_manage_single_organization_user_remove',
                         data={'org': self.unrelated_organization.pk},
                         reverse_kwargs={'args': [self.unrelated_organization_user.pk]},
                         require_status_code=404)

    def test_can_remove_self_from_organization(self):
        self.log_in_user(self.organization_user)
        self.submit_form('user_management_manage_single_organization_user_remove',
                         data={'org': self.organization.pk},
                         reverse_kwargs={'args': [self.organization_user.pk]},
                         success_url=reverse('create_link'))
        self.assertFalse(self.organization_user.organizations.filter(pk=self.organization.pk).exists())

    ### ADDING NEW USERS TO REGISTRARS ###

    def test_admin_user_can_add_new_user_to_registrar(self):
        self.log_in_user(self.admin_user)
        self.submit_form('user_management_registrar_user_add_user',
                         data={'a-registrar': self.registrar.pk,
                               'a-first_name': 'First',
                               'a-last_name': 'Last',
                               'a-email': 'doesnotexist@example.com'},
                         query_params={'email': 'doesnotexist@example.com'},
                         success_url=reverse('user_management_manage_registrar_user'),
                         success_query=LinkUser.objects.filter(email='doesnotexist@example.com',
                                                               registrar=self.registrar).exists())


    def test_registrar_user_can_add_new_user_to_registrar(self):
        self.log_in_user(self.registrar_user)
        self.submit_form('user_management_registrar_user_add_user',
                         data={'a-registrar': self.registrar.pk,
                               'a-first_name': 'First',
                               'a-last_name': 'Last',
                               'a-email': 'doesnotexist@example.com'},
                         query_params={'email': 'doesnotexist@example.com'},
                         success_url=reverse('user_management_manage_registrar_user'),
                         success_query=LinkUser.objects.filter(email='doesnotexist@example.com',
                                                               registrar=self.registrar).exists())

    def test_registrar_user_cannot_add_new_user_to_inaccessible_registrar(self):
        self.log_in_user(self.registrar_user)
        self.submit_form('user_management_registrar_user_add_user',
                         data={'a-registrar': self.unrelated_registrar.pk,
                               'a-first_name': 'First',
                               'a-last_name': 'Last',
                               'a-email': 'doesnotexist@example.com'},
                         query_params={'email': 'doesnotexist@example.com'},
                         error_keys=['registrar'])
        self.assertFalse(LinkUser.objects.filter(email='doesnotexist@example.com',
                                                 registrar=self.unrelated_registrar).exists())

    ### ADDING EXISTING USERS TO REGISTRARS ###

    def test_admin_user_can_add_existing_user_to_registrar(self):
        self.log_in_user(self.admin_user)
        self.submit_form('user_management_registrar_user_add_user',
                         data={'a-registrar': self.registrar.pk},
                         query_params={'email': self.regular_user.email},
                         success_url=reverse('user_management_manage_registrar_user'),
                         success_query=LinkUser.objects.filter(pk=self.regular_user.pk, registrar=self.registrar))

    def test_registrar_user_can_add_existing_user_to_registrar(self):
        self.log_in_user(self.registrar_user)
        self.submit_form('user_management_registrar_user_add_user',
                         data={'a-registrar': self.registrar.pk},
                         query_params={'email': self.regular_user.email},
                         success_url=reverse('user_management_manage_registrar_user'),
                         success_query=LinkUser.objects.filter(pk=self.regular_user.pk, registrar=self.registrar))

    def test_registrar_user_can_upgrade_org_user_to_registrar(self):
        self.log_in_user(self.registrar_user)
        self.submit_form('user_management_registrar_user_add_user',
                         data={'a-registrar': self.registrar.pk},
                         query_params={'email': self.organization_user.email},
                         success_url=reverse('user_management_manage_registrar_user'),
                         success_query=LinkUser.objects.filter(pk=self.organization_user.pk, registrar=self.registrar))
        self.assertFalse(LinkUser.objects.filter(pk=self.organization_user.pk, organizations=self.organization).exists())

    def test_registrar_user_cannot_upgrade_unrelated_org_user_to_registrar(self):
        self.log_in_user(self.registrar_user)
        resp = self.submit_form('user_management_registrar_user_add_user',
                                data={'a-registrar': self.registrar.pk},
                                query_params={'email': self.unrelated_organization_user.email})
        self.assertIn("belongs to organizations that are not controlled by your registrar", resp.content)
        self.assertFalse(LinkUser.objects.filter(pk=self.unrelated_organization_user.pk, registrar=self.registrar).exists())

    def test_registrar_user_cannot_add_existing_user_to_inaccessible_registrar(self):
        self.log_in_user(self.registrar_user)
        self.submit_form('user_management_registrar_user_add_user',
                         data={'a-registrar': self.unrelated_registrar.pk},
                         query_params={'email': self.regular_user.email},
                         error_keys=['registrar'])
        self.assertFalse(LinkUser.objects.filter(pk=self.regular_user.pk, registrar=self.unrelated_registrar).exists())

    def test_cannot_add_admin_user_to_registrar(self):
        self.log_in_user(self.registrar_user)
        resp = self.submit_form('user_management_registrar_user_add_user',
                         data={'a-registrar': self.registrar.pk},
                         query_params={'email': self.admin_user.email})
        self.assertIn("is an admin user", resp.content)
        self.assertFalse(LinkUser.objects.filter(pk=self.admin_user.pk, registrar=self.registrar).exists())

    def test_cannot_add_registrar_user_to_registrar(self):
        self.log_in_user(self.registrar_user)
        resp = self.submit_form('user_management_registrar_user_add_user',
                                data={'a-registrar': self.registrar.pk},
                                query_params={'email': self.unrelated_registrar_user.email})
        self.assertIn("is already a member of another registrar", resp.content)
        self.assertFalse(LinkUser.objects.filter(pk=self.unrelated_registrar_user.pk, registrar=self.registrar).exists())

    ### REMOVING USERS FROM REGISTRARS ###

    def test_can_remove_user_from_registrar(self):
        self.log_in_user(self.registrar_user)
        self.regular_user.registrar = self.registrar
        self.regular_user.save()
        self.submit_form('user_management_manage_single_registrar_user_remove',
                         reverse_kwargs={'args': [self.regular_user.pk]},
                         success_url=reverse('user_management_manage_registrar_user'))
        self.assertFalse(LinkUser.objects.filter(pk=self.regular_user.pk, registrar=self.registrar).exists())

    def test_registrar_cannot_remove_unrelated_user_from_registrar(self):
        self.log_in_user(self.registrar_user)
        self.submit_form('user_management_manage_single_registrar_user_remove',
                         reverse_kwargs={'args': [self.unrelated_registrar_user.pk]},
                         require_status_code=404)

    def test_can_remove_self_from_registrar(self):
        self.log_in_user(self.registrar_user)
        self.submit_form('user_management_manage_single_registrar_user_remove',
                         reverse_kwargs={'args': [self.registrar_user.pk]},
                         success_url=reverse('create_link'))
        self.assertFalse(LinkUser.objects.filter(pk=self.registrar_user.pk, registrar=self.registrar).exists())

    ### ADDING NEW USERS AS ADMINS ###

    def test_admin_user_can_add_new_user_as_admin(self):
        self.log_in_user(self.admin_user)
        self.submit_form('user_management_admin_user_add_user',
                         data={'a-first_name': 'First',
                               'a-last_name': 'Last',
                               'a-email': 'doesnotexist@example.com'},
                         query_params={'email': 'doesnotexist@example.com'},
                         success_url=reverse('user_management_manage_admin_user'),
                         success_query=LinkUser.objects.filter(email='doesnotexist@example.com',
                                                               is_staff=True).exists())
    ### ADDING EXISTING USERS AS ADMINS ###

    def test_admin_user_can_add_existing_user_as_admin(self):
        self.log_in_user(self.admin_user)
        self.submit_form('user_management_admin_user_add_user',
                         query_params={'email': self.regular_user.email},
                         success_url=reverse('user_management_manage_admin_user'),
                         success_query=LinkUser.objects.filter(pk=self.regular_user.pk, is_staff=True))

    ### REMOVING USERS AS ADMINS ###

    def test_can_remove_user_from_admin(self):
        self.log_in_user(self.admin_user)
        self.regular_user.is_staff = True
        self.regular_user.save()
        self.submit_form('user_management_manage_single_admin_user_remove',
                         reverse_kwargs={'args': [self.regular_user.pk]},
                         success_url=reverse('user_management_manage_admin_user'))
        self.assertFalse(LinkUser.objects.filter(pk=self.regular_user.pk, is_staff=True).exists())

    def test_can_remove_self_from_admin(self):
        self.log_in_user(self.admin_user)
        self.submit_form('user_management_manage_single_admin_user_remove',
                         reverse_kwargs={'args': [self.admin_user.pk]},
                         success_url=reverse('create_link'))
        self.assertFalse(LinkUser.objects.filter(pk=self.admin_user.pk, is_staff=True).exists())

    ### SETTINGS ###

    def test_user_can_change_own_settings(self):
        self.submit_form('user_management_settings_profile',
                         user=self.admin_user,
                         data={
                             'a-first_name': 'Newfirst',
                             'a-last_name': 'Newlast',
                             'a-email': 'test_admin_user@example.com'
                         },
                         success_url=reverse('user_management_settings_profile'),
                         success_query=LinkUser.objects.filter(first_name='Newfirst'))

    ### SIGNUP ###

    def test_account_creation_views(self):
        # user registration
        new_user_email = "new_email@test.com"
        self.submit_form('sign_up', {'email': new_user_email, 'first_name': 'Test', 'last_name': 'Test'},
                         success_url=reverse('register_email_instructions'),
                         success_query=LinkUser.objects.filter(email=new_user_email))

        confirmation_code = LinkUser.objects.get(email=new_user_email).confirmation_code

        # reg confirm - non-matching passwords
        self.submit_form('register_password', reverse_kwargs={'args': [confirmation_code]},
                         data={'new_password1':'a', 'new_password2':'b'},
                         error_keys=['new_password2'])

        # reg confirm - correct
        self.submit_form('register_password', reverse_kwargs={'args': [confirmation_code]},
                         data={'new_password1': 'a', 'new_password2': 'a'},
                         success_url=reverse('user_management_limited_login'))

    def test_signup_with_existing_email_rejected(self):
        self.submit_form('sign_up',
                         {'email': self.registrar_user.email, 'first_name': 'Test', 'last_name': 'Test'},
                         error_keys=['email'])

    def test_registration_confirmation_with_bad_code_rejected(self):
        response = self.submit_form('register_password', reverse_kwargs={'args':['bad_confirmation_code']})
        self.assertTrue('no_code' in response.context)

    ### ADMIN STATS ###

    def test_admin_stats(self):
        self.log_in_user(self.admin_user)
        self.get('user_management_stats', reverse_kwargs={'args':['days']})
        self.get('user_management_stats', reverse_kwargs={'args':['celery']})
        self.get('user_management_stats', reverse_kwargs={'args':['random']})
        self.get('user_management_stats', reverse_kwargs={'args':['emails']})
