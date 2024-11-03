<!--suppress JSUnusedLocalSymbols -->
<template>
  <v-card>
    <ac-load-section :controller="subjectHandler.user">
      <template v-slot:default>
        <v-card-text>
          <v-row dense>
            <v-col>
              <v-card-subtitle>Primary Credentials</v-card-subtitle>
            </v-col>
          </v-row>
          <v-row no-gutters class="pb-3">
            <v-col class="text-center" cols="12" sm="4" lg="4">
              <v-btn color="primary" @click="showUsernameChange=true" variant="elevated">Change Username</v-btn>
              <h3>Username: {{subject!.username}}</h3>
            </v-col>
            <v-col class="text-center" cols="12" sm="4" lg="4">
              <v-btn color="primary" @click="showPasswordChange=true" variant="elevated">Change Password</v-btn>
              <h3>Password</h3>
            </v-col>
            <v-col class="text-center" cols="12" sm="4" lg="4">
              <v-btn color="primary" @click="showEmailChange=true" variant="elevated">Change Email</v-btn>
              <h3>Email: {{userSubject.email}}</h3>
            </v-col>
          </v-row>
          <ac-form-dialog
              v-model="showUsernameChange"
              @submit.stop="usernameForm.submitThen(save)"
              v-bind="usernameForm.bind"
              title="Change Username"
          >
            <template v-slot:header>
              <v-row no-gutters>
                <v-col class="text-center" cols="12" md="6" offset-md="3">
                  <h3>
                    Warning: Any links to your account, characters, submissions, etc, such as from search engines or
                    other
                    sites,
                    will be broken by changing your username. This can affect SEO.
                  </h3>
                </v-col>
              </v-row>
            </template>
            <v-row no-gutters>
              <v-col cols="12" md="6" offset-md="3">
                <v-text-field
                    label="New Username"
                    v-bind="usernameForm.fields.username.bind"
                />
              </v-col>
              <v-col cols="12" md="6" offset-md="3">
                <v-text-field
                    label="Password"
                    type="password"
                    autocomplete="off"
                    hint="For security purposes, please enter your password to change your username."
                    v-bind="usernameForm.fields.current_password.bind"
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
            <v-row no-gutters>
              <v-col cols="12" md="6" offset-md="3">
                <v-text-field
                    label="Current Password"
                    type="password"
                    autocomplete="off"
                    hint="For security purposes, please enter your current password first."
                    v-bind="passwordForm.fields.current_password.bind"
                />
              </v-col>
              <v-col cols="12" md="6" offset-md="3">
                <v-text-field
                    label="New Password"
                    type="password"
                    autocomplete="off"
                    v-bind="passwordForm.fields.new_password.bind"
                />
              </v-col>
              <v-col cols="12" md="6" offset-md="3">
                <v-text-field
                    label="Confirm New Password"
                    type="password"
                    autocomplete="off"
                    v-bind="passwordForm.fields.new_password2.bind"
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
            <v-row no-gutters>
              <v-col cols="12" md="6" offset-md="3">
                <v-text-field
                    label="New Email"
                    type="email"
                    autocomplete="off"
                    v-bind="emailForm.fields.email.bind"
                />
              </v-col>
              <v-col cols="12" md="6" offset-md="3">
                <v-text-field
                    label="Confirm New Email"
                    type="email"
                    autocomplete="off"
                    v-bind="emailForm.fields.email2.bind"
                />
              </v-col>
              <v-col cols="12" md="6" offset-md="3">
                <v-text-field
                    label="Current Password"
                    type="password"
                    autocomplete="off"
                    hint="For security purposes, please enter your current password first."
                    v-bind="emailForm.fields.current_password.bind"
                />
              </v-col>
            </v-row>
          </ac-form-dialog>
          <v-row dense>
            <v-col cols="12">
              <v-card-subtitle>Two factor Authentication</v-card-subtitle>
            </v-col>
            <v-col cols="12">
              <v-divider/>
            </v-col>
            <v-col cols="12">
              <ac-setup-two-factor :username="username"/>
            </v-col>
            <v-col cols="12">
              <v-divider/>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12">
              <v-card-subtitle>Account Management</v-card-subtitle>
            </v-col>
            <v-col cols="12" class="text-center">
              <v-btn color="danger" @click="showDeleteAccount = true" variant="elevated">
                <v-icon left :icon="mdiDeleteForever"/>
                Delete my account.
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
                  <v-alert color="danger" :value="true" class="mt-2">
                    <template v-slot:prepend>
                      <v-icon :icon="mdiAlert" size="x-large" />
                    </template>
                    Account deletion is PERMANENT. To make sure this is not a mistake, please fill in the following
                    information to confirm. You must have no open orders and no outstanding balance before removing your
                    account.
                  </v-alert>
                </v-col>
                <v-col cols="12" md="6" offset-md="3">
                  <ac-bound-field :field="deleteUserForm.fields.username" label="Username"
                                  hint="The username of this account."/>
                </v-col>
                <v-col cols="12" md="6" offset-md="3">
                  <ac-bound-field :field="deleteUserForm.fields.email" label="Email"
                                  hint="The email we have on file for this account."/>
                </v-col>
                <v-col cols="12" md="6" offset-md="3">
                  <ac-bound-field :field="deleteUserForm.fields.password" type="password" label="Password"
                                  hint="Your current password."/>
                </v-col>
                <v-col cols="12" md="6" offset-md="3">
                  <ac-bound-field :field="deleteUserForm.fields.verify" label="I Am Absolutely Sure"
                                  field-type="v-checkbox"
                                  :persistent-hint="true"
                                  hint="I am absolutely sure that I want to delete my account. I understand that deletion
                                  is permanent and my account cannot be recovered."/>
                </v-col>
              </v-row>
            </template>
          </ac-form-dialog>
        </v-card-text>
      </template>
    </ac-load-section>
  </v-card>
</template>

<script setup lang="ts">
import {useSubject} from '@/mixins/subjective.ts'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import AcSetupTwoFactor from './AcSetupTwoFactor.vue'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import {useAlerts} from '@/mixins/alerts.ts'
import {mdiAlert, mdiDeleteForever} from '@mdi/js'
import {computed, ref, watch} from 'vue'
import {useForm} from '@/store/forms/hooks.ts'
import {AlertCategory} from '@/store/artState.ts'
import type {SubjectiveProps} from '@/types/main'
import {User} from '@/store/profiles/types/main'

const showUsernameChange = ref(false)
const showPasswordChange = ref(false)
const showEmailChange = ref(false)
const showDeleteAccount = ref(false)

const props = defineProps<SubjectiveProps>()

const {subject, subjectHandler} = useSubject({props, controlPowers: ['administrate_users']})

const userSubject = computed(() => subject.value as User)

const {sendAlert} = useAlerts()

const url = computed(() => {
  return `/api/profiles/account/${props.username}/auth/credentials/`
})

const deleteUrl = computed(() => {
  return `/api/profiles/account/${props.username}/auth/delete-account/`
})

const passwordDisabled = computed(() => {
  // This form is especially dangerous, so don't allow it to be sent without validation.
  if (passwordForm.disabled) {
    return true
  }
  if (!(passwordForm.fields.new_password.value && passwordForm.fields.current_password.value)) {
    return true
  }
  return passwordForm.fields.new_password.value !== passwordForm.fields.new_password2.value
})

const emailDisabled = computed(() => {
  // This form is especially dangerous, so don't allow it to be sent without validation.
  if (emailForm.disabled) {
    return true
  }
  if (!(emailForm.fields.email.value && emailForm.fields.current_password.value)) {
    return true
  }
  return emailForm.fields.email.value !== emailForm.fields.email2.value
})

const usernameForm = useForm('usernameChange', {
  endpoint: url.value,
  fields: {
    username: {
      value: '',
      validators: [{name: 'required'}, {
        name: 'username',
        async: true,
      }],
    },
    current_password: {
      value: '',
      validators: [{name: 'required'}],
    },
  },
})

const passwordForm = useForm('passwordChange', {
  endpoint: url.value,
  fields: {
    new_password: {
      value: '',
      validators: [{name: 'required'}, {
        name: 'password',
        async: true,
        args: ['password'],
      }],
    },
    new_password2: {
      value: '',
      validators: [
        {name: 'required'}, {
          name: 'matches',
          args: ['new_password', 'Passwords do not match.'],
        },
      ],
    },
    current_password: {
      value: '',
      validators: [{name: 'required'}],
    },
  },
})

const emailForm = useForm('emailChange', {
  endpoint: url.value,
  fields: {
    email: {
      value: '',
      validators: [{name: 'email'}, {
        name: 'email',
        async: true,
      }],
    },
    email2: {
      value: '',
      validators: [
        {name: 'required'}, {
          name: 'matches',
          args: ['email', 'Emails do not match.'],
        },
      ],
    },
    current_password: {
      value: '',
      validators: [{name: 'required'}],
    },
  },
})

const deleteUserForm = useForm('deleteUserAccount', {
  endpoint: deleteUrl.value,
  fields: {
    username: {
      value: '',
    },
    password: {
      value: '',
    },
    email: {
      value: '',
      validators: [{name: 'email'}, {name: 'email'}],
    },
    verify: {
      value: false,
    },
  },
})

const save = (response: User) => {
  subjectHandler.user.updateX(response)
  showUsernameChange.value = false
  showPasswordChange.value = false
  showEmailChange.value = false
  sendAlert({message: 'Account updated successfully!', category: AlertCategory.SUCCESS})
}

watch(url, (newVal: string) => {
  usernameForm.endpoint = newVal
  passwordForm.endpoint = newVal
  emailForm.endpoint = newVal
})

watch(deleteUrl, (newVal: string) => {
  deleteUserForm.endpoint = newVal
})


watch(() => passwordForm.fields.new_password.value, () => {
  if (passwordForm.fields.new_password.value) {
    passwordForm.fields.new_password2.validate()
  }
}, {deep: true})
</script>

<style scoped>

</style>
