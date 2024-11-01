<template>
  <v-container>
    <ac-load-section v-if="isSales" :controller="stats">
      <template v-slot:default>
        <v-row no-gutters class="text-center" v-if="stats.x">
          <v-col cols="12" md="6">
            <h1>
              <router-link style="text-decoration: underline;"
                           :to="{name: 'BuyAndSell', params: {question: 'workload-management'}}">
                Workload Management
              </router-link>
              Panel
            </h1>
            <v-row no-gutters>
              <v-col cols="6">Total Slots:</v-col>
              <v-col cols="6">{{ stats.x.max_load }}</v-col>
              <v-col cols="6">Slots filled:</v-col>
              <v-col cols="6">{{ stats.x.load }}</v-col>
              <v-col cols="6">Active Orders:</v-col>
              <v-col cols="6">{{ stats.x.active_orders }}</v-col>
              <v-col cols="6">New Orders:</v-col>
              <v-col cols="6">{{ stats.x.new_orders }}</v-col>
              <v-row class="pb-1" v-if="stats.x.escrow_enabled">
                <v-col cols="12">
                  <v-card>
                    <v-card-text>
                      To see details on your current bank settings and transfers,
                      visit your
                      <a href="https://connect.stripe.com/express_login">Stripe Express Dashboard</a>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
            </v-row>
          </v-col>
          <v-col cols="12" md="6" class="pb-2 d-flex flex-column">
            <div v-if="closed" class="pb-2">
              <strong>You are currently unable to take new commissions because:</strong>
              <ul>
                <li v-if="stats.x.delinquent">You have an unpaid invoice. Please find it in your
                  <router-link :to="{name: 'Invoices', params: {username}}">invoice list and pay it.</router-link>
                </li>
                <li v-if="stats.x.commissions_closed">You have set your 'commissions closed' setting.</li>
                <li v-if="stats.x.load >= stats.x.max_load">You have filled all of your slots. You can increase your
                  maximum slots to take on more commissions at one time in your artist settings.
                </li>
                <li v-else-if="stats.x.products_available === 0">You have no products available for customers to
                  purchase. This
                  may mean there are none, they are hidden, they have reached their 'Max at Once' level, or you do not
                  have
                  enough slots to take any of your existing products on.
                </li>
              </ul>
            </div>
            <div v-else>
              <p>You are currently able to take commissions.
                <router-link :to="{name: 'Store', params: {username}}">Manage your store here.</router-link>
              </p>
              <div class="py-5 d-none d-md-flex"></div>
            </div>
            <div class="grow"></div>
            <div class="align-self-center justify-end pb-2">
              <v-row>
                <v-col class="text-center d-flex">
                  <v-btn
                      color="green" :to="{name: 'InvoiceByProduct', params: {username}}" variant="elevated" class="new-invoice-button"
                  >
                    <v-icon left :icon="mdiReceipt"/>
                    New Invoice
                  </v-btn>
                </v-col>
                <v-col class="text-center">
                  <v-btn color="primary" @click="showBroadcast = true" variant="elevated">
                    <v-icon left :icon="mdiBullhorn"/>
                    Broadcast to buyers
                  </v-btn>
                </v-col>
              </v-row>
            </div>
          </v-col>
        </v-row>
      </template>
    </ac-load-section>
    <v-tabs fixed-tabs>
      <v-tab :to="{name: 'Current' + baseName, params: {username}}">Current</v-tab>
      <v-tab v-if="!isCases" :to="{name: 'Waiting' + baseName, params: {username}}">Waiting</v-tab>
      <v-tab :to="{name: 'Archived' + baseName, params: {username}}">Archived</v-tab>
      <v-tab v-if="!isCases" :to="{name: 'Cancelled' + baseName, params: {username}}">Cancelled</v-tab>
    </v-tabs>
    <v-window>
      <router-view :key="route.path"></router-view>
    </v-window>
    <ac-form-dialog v-if="isSales" v-bind="broadcastForm.bind" v-model="showBroadcast"
                    @submit.prevent="broadcastForm.submitThen(() => {confirmBroadcast = true})">
      <v-row v-if="!confirmBroadcast">
        <v-col cols="12" class="text-center">
          <h1>Add a comment to all of your orders at once.</h1>
        </v-col>
        <v-col cols="12" sm="6">
          <ac-bound-field field-type="ac-checkbox"
                          label="Include Active Orders"
                          :field="broadcastForm.fields.include_active"
                          help-text="Send this message to all open orders."/>
        </v-col>
        <v-col cols="12" sm="6">
          <ac-bound-field
              field-type="ac-checkbox"
              label="Include Waitlist"
              help-text="Send this message to all orders that are in your waitlist."
              :field="broadcastForm.fields.include_waitlist"
          />
        </v-col>
        <v-col cols="12">
          <ac-bound-field field-type="ac-editor" :field="broadcastForm.fields.text" :save-indicator="false"/>
        </v-col>
      </v-row>
      <v-row v-else>
        <v-col cols="12" class="text-center">
          <span class="title">Broadcast sent!</span>
        </v-col>
        <v-col cols="12" class="text-center">
          <v-icon x-large color="green" :icon="mdiCheckCircle"/>
        </v-col>
      </v-row>
      <template v-slot:bottom-buttons v-if="confirmBroadcast">
        <v-card-actions row wrap class="hidden-sm-and-down">
        </v-card-actions>
      </template>
      <template v-slot:top-buttons v-if="confirmBroadcast">
        <v-card-actions row wrap class="hidden-sm-and-down">
        </v-card-actions>
      </template>
    </ac-form-dialog>
  </v-container>
</template>

<script setup lang="ts">
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import {useSubject} from '@/mixins/subjective.ts'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import {flatten, getSalesStatsSchema} from '@/lib/lib.ts'
import {mdiCheckCircle, mdiBullhorn, mdiReceipt} from '@mdi/js'
import {computed, ref} from 'vue'
import {useSingle} from '@/store/singles/hooks.ts'
import {listenForList} from '@/store/lists/hooks.ts'
import {useForm} from '@/store/forms/hooks.ts'
import {useRoute, useRouter} from 'vue-router'
import {usePricing} from '@/mixins/PricingAware.ts'
import type {CommissionStats, SubjectiveProps} from '@/types/main'


const props = defineProps<{baseName: string} & SubjectiveProps>()
const {subjectHandler} = useSubject({ props })
const route = useRoute()
const router = useRouter()
const showBroadcast = ref(false)
const confirmBroadcast = ref(false)

const type = props.baseName.toLocaleLowerCase()
const stats = useSingle<CommissionStats>(`stats__sales__${flatten(props.username)}`, getSalesStatsSchema(props.username))
listenForList(`orders__${flatten(props.username)}__${type}__archived`)
listenForList(`orders__${flatten(props.username)}__${type}__current`)
listenForList(`orders__${flatten(props.username)}__${type}__waiting`)

const isSales = computed(() => props.baseName === 'Sales')

const isCases = computed(() => props.baseName === 'Cases')

const isCurrentRoute = computed(() => route.name === props.baseName)

if (isCurrentRoute.value) {
  router.replace({
    name: 'Current' + props.baseName,
    params: {username: props.username},
  })
}
if (isSales.value) {
  stats.get()
  subjectHandler.artistProfile.get()
}
const broadcastForm = useForm('broadcast', {
  endpoint: `/api/sales/account/${props.username}/broadcast/`,
  fields: {
    text: {value: ''},
    extra_data: {value: {}},
    include_active: {value: true},
    include_waitlist: {value: false},
  },
})

const closed = computed(() => {
  if (!stats.x) {
    return null
  }
  return stats.x.commissions_closed || stats.x.commissions_disabled || stats.x.load >= stats.x.max_load
})
// Used by tests.
const {pricing} = usePricing()
</script>
