<!--suppress JSUnusedLocalSymbols -->
<template>
  <v-card>
    <ac-load-section :controller="subjectHandler.user">
      <template v-slot:default>
        <v-card-text>
          <v-subheader>Primary Credentials</v-subheader>
          <v-row no-gutters   class="pb-3">
            <v-col class="text-center" cols="12" sm="4" lg="4" >
              <v-btn color="primary" @click="showUsernameChange=true">Change Username</v-btn>
              <h3>Username: {{subject.username}}</h3>
            </v-col>
            <v-col class="text-center" cols="12" sm="4" lg="4" >
              <v-btn color="primary" @click="showPasswordChange=true">Change Password</v-btn>
              <h3>Password</h3>
            </v-col>
            <v-col class="text-center" cols="12" sm="4" lg="4" >
              <v-btn color="primary" @click="showEmailChange=true">Change Email</v-btn>
              <h3>Email: {{subject.email}}</h3>
            </v-col>
          </v-row>
          <ac-form-dialog
              v-model="showUsernameChange"
              @submit.stop="usernameForm.submitThen(save)"
              v-bind="usernameForm.bind"
              title="Change Username"
          >
            <v-row no-gutters slot="header"  >
              <v-col class="text-center" cols="12" md="6" offset-md="3">
                <h3>
                  Warning: Any links to your account, characters, submissions, etc, such as from search engines or other
                  sites,
                  will be broken by changing your username. This can affect SEO.
                </h3>
              </v-col>
            </v-row>
            <v-row no-gutters  >
              <v-col cols="12" md="6" offset-md="3">
                <v-text-field
                    label="New Username"
                    v-bind="usernameForm.fields.username.bind"
                    v-on="usernameForm.fields.username.on"
                />
              </v-col>
              <v-col cols="12" md="6" offset-md="3">
                <v-text-field
                    label="Password"
                    type="password"
                    autocomplete="off"
                    hint="For security purposes, please enter your password to change your username."
                    v-bind="usernameForm.fields.current_password.bind"
                    v-on="usernameForm.fields.current_password.on"
                />
              </v-col>
            </v-row>
          </ac-form-dialog>
          <ac-form-dialog
              v-model="showPasswordChange"
              @submit.prevent="passwordForm.submitThen(save)"
              v-bind="passwordForm.bind"
              title="Change Password"
              :disabled="passwordDisabled"
          >
            <v-row no-gutters  >
              <v-col cols="12" md="6" offset-md="3">
                <v-text-field
                    label="Current Password"
                    type="password"
                    autocomplete="off"
                    hint="For security purposes, please enter your current password first."
                    v-bind="passwordForm.fields.current_password.bind"
                    v-on="passwordForm.fields.current_password.on"
                />
              </v-col>
              <v-col cols="12" md="6" offset-md="3">
                <v-text-field
                    label="New Password"
                    type="password"
                    autocomplete="off"
                    v-bind="passwordForm.fields.new_password.bind"
                    v-on="passwordForm.fields.new_password.on"
                />
              </v-col>
              <v-col cols="12" md="6" offset-md="3">
                <v-text-field
                    label="Confirm New Password"
                    type="password"
                    autocomplete="off"
                    v-bind="passwordForm.fields.new_password2.bind"
                    v-on="passwordForm.fields.new_password2.on"
                />
              </v-col>
            </v-row>
          </ac-form-dialog>
          <ac-form-dialog
              v-model="showEmailChange"
              @submit.prevent="emailForm.submitThen(save)"
              v-bind="emailForm.bind"
              :disabled="emailDisabled"
              title="Change Email"
          >
            <v-row no-gutters  >
              <v-col cols="12" md="6" offset-md="3">
                <v-text-field
                    label="New Email"
                    type="email"
                    autocomplete="off"
                    v-bind="emailForm.fields.email.bind"
                    v-on="emailForm.fields.email.on"
                />
              </v-col>
              <v-col cols="12" md="6" offset-md="3">
                <v-text-field
                    label="Confirm New Email"
                    type="email"
                    autocomplete="off"
                    v-bind="emailForm.fields.email2.bind"
                    v-on="emailForm.fields.email2.on"
                />
              </v-col>
              <v-col cols="12" md="6" offset-md="3">
                <v-text-field
                    label="Current Password"
                    type="password"
                    autocomplete="off"
                    hint="For security purposes, please enter your current password first."
                    v-bind="emailForm.fields.current_password.bind"
                    v-on="emailForm.fields.current_password.on"
                />
              </v-col>
            </v-row>
          </ac-form-dialog>
          <v-divider />
          <v-subheader>Two factor Authentication</v-subheader>
          <ac-setup-two-factor :username="username" />
          <v-divider />
          <v-subheader>Account Management</v-subheader>
          <v-row>
            <v-col cols="12" class="text-center">
              <v-btn color="danger" @click="showDeleteAccount = true">
                <v-icon left>delete_forever</v-icon>Delete my account.
              </v-btn>
            </v-col>
          </v-row>
          <ac-form-dialog
              v-model="showDeleteAccount"
              title="Delete my account."
              @submit.prevent="deleteUserForm.submitThen(() => undefined)"
              v-bind="deleteUserForm.bind"
          >
            <template v-slot:default>
              <v-row>
                <v-col cols="12">
                  <v-alert color="danger" icon="warning" :value="true" class="mt-2">
                    Account deletion is PERMANENT. To make sure this is not a mistake, please fill in the following
                    information to confirm. You must have no open orders and no outstanding balance before removing your
                    account.
                  </v-alert>
                </v-col>
                <v-col cols="12" md="6" offset-md="3">
                  <ac-bound-field :field="deleteUserForm.fields.username" label="Username" hint="The username of this account." />
                </v-col>
                <v-col cols="12" md="6" offset-md="3">
                  <ac-bound-field :field="deleteUserForm.fields.email" label="Email" hint="The email we have on file for this account." />
                </v-col>
                <v-col cols="12" md="6" offset-md="3">
                  <ac-bound-field :field="deleteUserForm.fields.password" type="password" label="Password" hint="Your current password." />
                </v-col>
                <v-col cols="12" md="6" offset-md="3">
                  <ac-bound-field :field="deleteUserForm.fields.verify" label="I Am Absolutely Sure"
                                  field-type="v-checkbox"
                                  :persistent-hint="true"
                                  hint="I am absolutely sure that I want to delete my account. I understand that deletion
                                  is permanent and my account cannot be recovered." />
                </v-col>
              </v-row>
            </template>
          </ac-form-dialog>
        </v-card-text>
      </template>
    </ac-load-section>
  </v-card>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Subjective from '@/mixins/subjective'
import {FormController} from '@/store/forms/form-controller'
import {Watch} from 'vue-property-decorator'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import AcSetupTwoFactor from './AcSetupTwoFactor.vue'
import {User} from '@/store/profiles/types/User'
import Alerts from '@/mixins/alerts'
import AcBoundField from '@/components/fields/AcBoundField'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'

  @Component({
    components: {AcLoadSection, AcBoundField, AcSetupTwoFactor, AcFormDialog},
  })
export default class Credentials extends mixins(Subjective, Alerts) {
    private showSuccess: boolean = false
    private showUsernameChange: boolean = false
    private showPasswordChange: boolean = false
    private showEmailChange: boolean = false
    private showDeleteAccount: boolean = false
    private usernameForm: FormController = null as unknown as FormController
    private passwordForm: FormController = null as unknown as FormController
    private emailForm: FormController = null as unknown as FormController
    private deleteUserForm: FormController = null as unknown as FormController

    public created() {
      this.usernameForm = this.$getForm('usernameChange', {
        endpoint: this.url,
        fields: {
          username: {value: '', validators: [{name: 'required'}, {name: 'username', async: true}]},
          current_password: {value: '', validators: [{name: 'required'}]},
        },
      })
      this.passwordForm = this.$getForm('passwordChange', {
        endpoint: this.url,
        fields: {
          new_password: {
            value: '', validators: [{name: 'required'}, {name: 'password', async: true, args: ['password']}],
          },
          new_password2: {
            value: '',
            validators: [
              {name: 'required'}, {name: 'matches', args: ['new_password', 'Passwords do not match.']},
            ],
          },
          current_password: {value: '', validators: [{name: 'required'}]},
        },
      })
      this.emailForm = this.$getForm('emailChange', {
        endpoint: this.url,
        fields: {
          email: {
            value: '', validators: [{name: 'email'}, {name: 'email', async: true}],
          },
          email2: {
            value: '',
            validators: [
              {name: 'required'}, {name: 'matches', args: ['email', 'Emails do not match.']},
            ],
          },
          current_password: {value: '', validators: [{name: 'required'}]},
        },
      })
      this.deleteUserForm = this.$getForm('deleteUserAccount', {
        endpoint: this.deleteUrl,
        fields: {
          username: {
            value: '',
          },
          password: {
            value: ''
          },
          email: {
            value: '', validators: [{name: 'email'}, {name: 'email'}],
          },
          verify: {
            value: false,
          }
        },
      })
    }

    private save(response: User) {
      this.subjectHandler.user.updateX(response)
      this.showUsernameChange = false
      this.showPasswordChange = false
      this.showEmailChange = false
      this.$alert({message: 'Account updated successfully!'})
    }

    @Watch('url')
    private updateFormUrl(newVal: string) {
      this.usernameForm.endpoint = newVal
      this.passwordForm.endpoint = newVal
      this.emailForm.endpoint = newVal
    }

    @Watch('deleteUrl')
    private updateDeleteFormUrl(newVal: string) {
      this.deleteUserForm.endpoint = newVal
    }

    @Watch('passwordForm.fields.new_password.value', {deep: true})
    private validateSync() {
      const passwordForm = this.passwordForm as FormController
      if (passwordForm.fields.new_password.value) {
        passwordForm.fields.new_password2.validate()
      }
    }

    public get url() {
      return `/api/profiles/v1/account/${this.username}/auth/credentials/`
    }

    public get deleteUrl() {
      return `/api/profiles/v1/account/${this.username}/auth/delete-account/`
    }

    private get passwordDisabled() {
      // This form is especially dangerous, so don't allow it to be sent without validation.
      const passwordForm = this.passwordForm as FormController
      if (passwordForm.disabled) {
        return true
      }
      if (!(passwordForm.fields.new_password.value && passwordForm.fields.current_password.value)) {
        return true
      }
      return passwordForm.fields.new_password.value !== passwordForm.fields.new_password2.value
    }

    private get emailDisabled() {
      // This form is especially dangerous, so don't allow it to be sent without validation.
      const emailForm = this.emailForm as FormController
      if (emailForm.disabled) {
        return true
      }
      if (!(emailForm.fields.email.value && emailForm.fields.current_password.value)) {
        return true
      }
      return emailForm.fields.email.value !== emailForm.fields.email2.value
    }
}
</script>

<style scoped>

</style>
