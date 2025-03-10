<template>
  <ac-load-section :controller="validator">
    <template #default>
      <v-row
        no-gutters
        class="mt-5"
      >
        <v-col
          class="text-center"
          cols="12"
          md="6"
          offset-md="3"
        >
          <ac-form @submit.prevent="resetForm.submitThen(postReset)">
            <ac-form-container
              v-if="validator.x"
              class="mt-3"
              :sending="resetForm.sending"
              :errors="resetForm.errors"
            >
              <v-row no-gutters>
                <v-col cols="12">
                  <p>Reset password for {{ username }}</p>
                </v-col>
                <v-col cols="12">
                  <ac-bound-field
                    :field="resetForm.fields.new_password"
                    type="password"
                    label="New Password"
                  />
                </v-col>
                <v-col cols="12">
                  <ac-bound-field
                    :field="resetForm.fields.new_password2"
                    type="password"
                    label="New Password (again)"
                  />
                </v-col>
                <v-col
                  class="text-center"
                  cols="12"
                >
                  <v-btn
                    type="submit"
                    color="primary"
                    variant="flat"
                  >
                    Reset Password
                  </v-btn>
                </v-col>
              </v-row>
            </ac-form-container>
          </ac-form>
        </v-col>
      </v-row>
    </template>
    <template #failure>
      <v-container>
        <v-row no-gutters>
          <v-col
            class="text-center"
            cols="12"
            md="6"
            offset-md="3"
          >
            <v-alert
              value="error"
              type="error"
            >
              Your reset token is invalid or has expired.
              <router-link :to="{name: 'Forgot'}">
                You can request a new one here!
              </router-link>
            </v-alert>
          </v-col>
        </v-row>
      </v-container>
    </template>
  </ac-load-section>
</template>

<script setup lang="ts">
import AcLoadSection from '../wrappers/AcLoadSection.vue'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import {useViewer} from '@/mixins/viewer.ts'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import AcForm from '@/components/wrappers/AcForm.vue'
import {useSingle} from '@/store/singles/hooks.ts'
import {useForm} from '@/store/forms/hooks.ts'
import {useRouter} from 'vue-router'
import {User} from '@/store/profiles/types/main'


const props = defineProps<{resetToken: string, username: string}>()
const router = useRouter()
const {viewer, viewerHandler} = useViewer()

const validator = useSingle<any>(
    'passwordToken', {
      endpoint: `/api/profiles/forgot-password/token-check/${props.username}/${props.resetToken}/`,
    },
)
validator.get()
const resetForm = useForm(
    'passwordReset', {
      endpoint: `/api/profiles/forgot-password/perform-reset/${props.username}/${props.resetToken}/`,
      fields: {
        new_password: {value: ''},
        new_password2: {
          value: '',
          validators: [{
            name: 'matches',
            args: ['new_password', 'Passwords do not match.'],
          }],
        },
      },
    },
)

const postReset = (response: User) => {
  viewerHandler.user.x = response
  router.push(
      {
        name: 'Profile',
        params: {username: (viewer.value as User).username},
        query: {editing: 'true'},
      },
  )
}
</script>
