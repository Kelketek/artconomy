<template>
  <ac-load-section :controller="subjectHandler.user">
    <template #default>
      <v-row no-gutters>
        <v-col cols="12">
          <v-card>
            <v-card-text>
              <v-col
                class="text-center"
                cols="12"
              >
                <p><strong>Your default card will be charged for subscription services.</strong></p>
              </v-col>
              <ac-load-section :controller="clientSecret">
                <template #default>
                  <ac-form @submit.prevent="submitNewCard">
                    <ac-form-container v-bind="ccForm.bind">
                      <ac-card-manager
                        ref="cardManager"
                        :username="username"
                        :cc-form="ccForm"
                        :show-save="false"
                        :field-mode="false"
                        :show-all="true"
                        :save-only="true"
                        :client-secret="(clientSecret.x && clientSecret.x.secret) || ''"
                        @card-added="fetchSecret"
                      >
                        <template #new-card-button>
                          <v-col
                            class="text-center"
                            cols="12"
                          >
                            <v-btn
                              color="primary"
                              type="submit"
                              class="add-card-button"
                              variant="flat"
                            >
                              Add Card
                            </v-btn>
                          </v-col>
                        </template>
                      </ac-card-manager>
                    </ac-form-container>
                  </ac-form>
                </template>
              </ac-load-section>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </template>
  </ac-load-section>
</template>

<script setup lang="ts">
import {baseCardSchema, flatten} from '@/lib/lib.ts'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcForm from '@/components/wrappers/AcForm.vue'
import {computed, ComputedRef, ref, defineAsyncComponent, watch} from 'vue'
import {useSingle} from '@/store/singles/hooks.ts'
import {useViewer} from '@/mixins/viewer.ts'
import {useForm} from '@/store/forms/hooks.ts'
import {useList} from '@/store/lists/hooks.ts'
import {useSubject} from '@/mixins/subjective.ts'
import type AcCardManagerType from '@/components/views/settings/payment/AcCardManager.vue'
import type {ClientSecret, CreditCardToken, SubjectiveProps} from '@/types/main'
import {User} from '@/store/profiles/types/main'
const AcCardManager = defineAsyncComponent(() => import('@/components/views/settings/payment/AcCardManager.vue'))


const props = defineProps<SubjectiveProps>()
const {subjectHandler} = useSubject({ props })

const url = computed(() => {
  return `/api/sales/account/${props.username}/cards/`
})

const schema = baseCardSchema(url.value)
delete schema.fields.save_card
const clientSecret = useSingle<ClientSecret>(
  `${flatten(props.username)}__new_card__clientSecret`, {
    endpoint: `/api/sales/account/${props.username}/cards/setup-intent/`,
})

const cardManager = ref<null|typeof AcCardManagerType>(null)

const fetchSecret = () => {
  clientSecret.fetching = true
  clientSecret.post().then(clientSecret.makeReady)
}
fetchSecret()
const ccForm = useForm(flatten(`${flatten(props.username)}__cards__new`), baseCardSchema(url.value))
const viewerItems = useViewer()
const viewer = viewerItems.viewer as ComputedRef<User>
const cards = useList<CreditCardToken>(`${flatten(props.username)}__creditCards`, {
  endpoint: url.value,
  paginated: false,
  socketSettings: {
    appLabel: 'sales',
    modelName: 'CreditCardToken',
    serializer: 'CardSerializer',
    list: {
      appLabel: 'profiles',
      modelName: 'User',
      pk: viewer.value.id + '',
      listName: 'all_cards',
    },
  },
})
cards.firstRun()

const submitNewCard = () => {
  if (cardManager.value) {
    cardManager.value.stripeSubmit()
  }
}

watch(() => props.username, () => {
  cards.endpoint = url.value
})
</script>
