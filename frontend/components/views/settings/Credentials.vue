<!--suppress JSUnusedLocalSymbols -->
<template>
  <v-card>
    <v-card-text>
      <v-subheader>Primary Credentials</v-subheader>
      <v-layout row wrap class="pb-3">
        <v-flex xs12 sm4 lg4 text-xs-center>
          <v-btn color="primary" @click="showUsernameChange=true">Change Username</v-btn>
          <h3>Username: {{subject.username}}</h3>
        </v-flex>
        <v-flex xs12 sm4 lg4 text-xs-center>
          <v-btn color="primary" @click="showPasswordChange=true">Change Password</v-btn>
          <h3>Password</h3>
        </v-flex>
        <v-flex xs12 sm4 lg4 text-xs-center>
          <v-btn color="primary" @click="showEmailChange=true">Change Email</v-btn>
          <h3>Email: {{subject.email}}</h3>
        </v-flex>
      </v-layout>
      <ac-form-dialog
          v-model="showUsernameChange"
          @submit.stop="usernameForm.submitThen(save)"
          v-bind="usernameForm.bind"
          title="Change Username"
      >
        <v-layout slot="header" row wrap>
          <v-flex class="text-xs-center" xs12 md6 offset-md3>
            <h3>
              Warning: Any links to your account, characters, submissions, etc, such as from search engines or other
              sites,
              will be broken by changing your username. This can affect SEO.
            </h3>
          </v-flex>
        </v-layout>
        <v-layout row wrap>
          <v-flex xs12 md6 offset-md3>
            <v-text-field
                label="New Username"
                v-bind="usernameForm.fields.username.bind"
                v-on="usernameForm.fields.username.on"
            ></v-text-field>
          </v-flex>
          <v-flex xs12 md6 offset-md3>
            <v-text-field
                label="Password"
                type="password"
                autocomplete="off"
                hint="For security purposes, please enter your password to change your username."
                v-bind="usernameForm.fields.current_password.bind"
                v-on="usernameForm.fields.current_password.on"
            ></v-text-field>
          </v-flex>
        </v-layout>
      </ac-form-dialog>
      <ac-form-dialog
          v-model="showPasswordChange"
          @submit.prevent="passwordForm.submitThen(save)"
          v-bind="passwordForm.bind"
          title="Change Password"
          :disabled="passwordDisabled"
      >
        <v-layout row wrap>
          <v-flex xs12 md6 offset-md3>
            <v-text-field
                label="Current Password"
                type="password"
                autocomplete="off"
                hint="For security purposes, please enter your current password first."
                v-bind="passwordForm.fields.current_password.bind"
                v-on="passwordForm.fields.current_password.on"
            ></v-text-field>
          </v-flex>
          <v-flex xs12 md6 offset-md3>
            <v-text-field
                label="New Password"
                type="password"
                autocomplete="off"
                v-bind="passwordForm.fields.new_password.bind"
                v-on="passwordForm.fields.new_password.on"
            ></v-text-field>
          </v-flex>
          <v-flex xs12 md6 offset-md3>
            <v-text-field
                label="Confirm New Password"
                type="password"
                autocomplete="off"
                v-bind="passwordForm.fields.new_password2.bind"
                v-on="passwordForm.fields.new_password2.on"
            ></v-text-field>
          </v-flex>
        </v-layout>
      </ac-form-dialog>
      <ac-form-dialog
          v-model="showEmailChange"
          @submit.prevent="emailForm.submitThen(save)"
          v-bind="emailForm.bind"
          :disabled="emailDisabled"
          title="Change Email"
      >
        <v-layout row wrap>
          <v-flex xs12 md6 offset-md3>
            <v-text-field
                label="New Email"
                type="email"
                autocomplete="off"
                v-bind="emailForm.fields.email.bind"
                v-on="emailForm.fields.email.on"
            ></v-text-field>
          </v-flex>
          <v-flex xs12 md6 offset-md3>
            <v-text-field
                label="Confirm New Email"
                type="email"
                autocomplete="off"
                v-bind="emailForm.fields.email2.bind"
                v-on="emailForm.fields.email2.on"
            ></v-text-field>
          </v-flex>
          <v-flex xs12 md6 offset-md3>
            <v-text-field
                label="Current Password"
                type="password"
                autocomplete="off"
                hint="For security purposes, please enter your current password first."
                v-bind="emailForm.fields.current_password.bind"
                v-on="emailForm.fields.current_password.on"
            ></v-text-field>
          </v-flex>
        </v-layout>
      </ac-form-dialog>
      <v-divider></v-divider>
      <v-subheader>Two factor Authentication</v-subheader>
      <ac-setup-two-factor :username="username"></ac-setup-two-factor>
    </v-card-text>
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

  @Component({
    components: {AcSetupTwoFactor, AcFormDialog},
  })
export default class Credentials extends mixins(Subjective, Alerts) {
    private showSuccess: boolean = false
    private showUsernameChange: boolean = false
    private showPasswordChange: boolean = false
    private showEmailChange: boolean = false
    private usernameForm: FormController = null as unknown as FormController
    private passwordForm: FormController = null as unknown as FormController
    private emailForm: FormController = null as unknown as FormController

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

    @Watch('passwordForm.fields.new_password.value', {deep: true})
    private validateSync() {
      const passwordForm = this.passwordForm as FormController
      if (passwordForm.fields.new_password.value) {
        passwordForm.fields.new_password2.validate()
      }
    }

    public get url() {
      return `/api/profiles/v1/account/${this.subject && this.subject.username}/auth/credentials/`
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
