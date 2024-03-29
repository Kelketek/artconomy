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
      <router-view :key="$route.path"></router-view>
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

<script lang="ts">
import AcLoadSection from '../../wrappers/AcLoadSection.vue'
import {Component, mixins, Prop, toNative} from 'vue-facing-decorator'
import Subjective from '../../../mixins/subjective.ts'
import AcPaginated from '../../wrappers/AcPaginated.vue'
import {SingleController} from '@/store/singles/controller.ts'
import CommissionStats from '@/types/CommissionStats.ts'
import {FormController} from '@/store/forms/form-controller.ts'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import AcPricePreview from '@/components/price_preview/AcPricePreview.vue'
import {flatten, getSalesStatsSchema} from '@/lib/lib.ts'
import {mdiCheckCircle, mdiBullhorn, mdiReceipt} from '@mdi/js'

@Component({
  components: {
    AcPricePreview,
    AcBoundField,
    AcFormDialog,
    AcPaginated,
    AcLoadSection,
  },
})
class Orders extends mixins(Subjective) {
  public stats: SingleController<CommissionStats> = null as unknown as SingleController<CommissionStats>
  @Prop({required: true})
  public baseName!: string
  public showBroadcast = false
  public confirmBroadcast = false
  public broadcastForm: FormController = null as unknown as FormController
  public mdiCheckCircle = mdiCheckCircle
  public mdiBullhorn = mdiBullhorn
  public mdiReceipt = mdiReceipt

  public get isSales() {
    return this.baseName === 'Sales'
  }

  public get isCases() {
    return this.baseName === 'Cases'
  }

  public get isCurrentRoute() {
    return this.$route.name === this.baseName
  }

  // @ts-ignore
  public get sellerName() {
    return this.username
  }

  // @ts-ignore
  public get international() {
    return this.subject?.international || false
  }

  public get planName() {
    // eslint-disable-next-line camelcase
    return this.subject?.service_plan || null
  }

  public get closed() {
    const stats = this.stats.x as CommissionStats
    if (!stats) {
      return null
    }
    return stats.commissions_closed || stats.commissions_disabled || stats.load >= stats.max_load
  }

  public created() {
    const type = this.baseName.toLocaleLowerCase()
    this.stats = this.$getSingle(`stats__sales__${flatten(this.username)}`, getSalesStatsSchema(this.username))
    this.$listenForList(`orders__${flatten(this.username)}__${type}__archived`)
    this.$listenForList(`orders__${flatten(this.username)}__${type}__current`)
    this.$listenForList(`orders__${flatten(this.username)}__${type}__waiting`)
    if (this.isCurrentRoute) {
      this.$router.replace({
        name: 'Current' + this.baseName,
        params: {username: this.username},
      })
    }
    if (this.isSales) {
      this.stats.get()
      this.subjectHandler.artistProfile.get()
    }
    this.broadcastForm = this.$getForm('broadcast', {
      endpoint: `/api/sales/account/${this.username}/broadcast/`,
      fields: {
        text: {value: ''},
        extra_data: {value: {}},
        include_active: {value: true},
        include_waitlist: {value: false},
      },
    })
  }
}

export default toNative(Orders)
</script>
