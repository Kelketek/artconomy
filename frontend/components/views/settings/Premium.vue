<template>
  <v-card>
    <v-card-text>
      <v-row no-gutters v-if="!(subjectPlan && (subjectPlan.monthly_charge || subjectPlan.per_deliverable_price))">
        <v-col class="text-center" cols="12">
          <p>Premium settings are only available with a subscription.</p>
          <v-btn :to="{name: 'Upgrade'}" variant="flat" color="secondary">Upgrade Now!</v-btn>
        </v-col>
      </v-row>
      <v-row v-if="subjectPlan && subjectPlan.paypal_invoicing">
        <v-col class="text-center" cols="12">
          <v-list-subheader>PayPal Integration</v-list-subheader>
          <v-btn color="primary" variant="flat" type="submit" @click="showPaypal = true">Configure PayPal Integration</v-btn>
        </v-col>
      </v-row>
      <v-row v-if="subject && subject.landscape">
        <v-col class="text-center" cols="2">
          <v-icon size="x-large" :icon="siDiscord.path" />
        </v-col>
        <v-col class="text-center" cols="10">
          To get your special Discord role, <a href="https://discord.gg/4nWK9mf">join the Discord</a>, follow the
          instructions in the Welcome room, and, after admission, give Fox this URL: <br/>
        </v-col>
        <v-col cols="12">
          <v-text-field :disabled="true" :value="adminPath"/>
        </v-col>
      </v-row>
      <ac-form-dialog
          v-model="showPaypal"
          :large="true" v-bind="paypalForm.bind"
          :show-submit="paypalWarned || paypal.ready"
          title="PayPal Integration"
          @submit.prevent="paypalForm.submitThen(paypal.makeReady)"
          :cancel-text="paypal.ready ? 'Done' : 'Cancel'"
      >
        <v-card-text>
          <v-row v-if="!paypalWarned && !paypal.ready">
            <v-col cols="12">
              <span class="title">Notice</span>
              <p>
                This will integrate your Artconomy account with PayPal. Integrating with PayPal will allow you to
                automatically generate PayPal invoices on orders.
                Please note the following:
              </p>
              <ul>
                <li>Orders which use PayPal invoicing are not covered by Shield Protection.</li>
                <li>You can choose which orders use Shield and which orders use PayPal as your needs dictate.</li>
                <li>When you enable this feature, all orders which are not shield protected will use Paypal invoicing by
                  default.
                  You can disable this on a per-product and per-order basis.
                </li>
                <li>You <strong>MUST</strong> have a PayPal business account for this to work.</li>
                <li>PayPal's terms of service is hostile toward NSFW art commissions in most or all jurisdictions and
                  circumstances.
                  <strong>You should not use PayPal to track NSFW art commissions. If you do so, you do so at your own
                    risk!</strong></li>
                <li>Invoices generated in PayPal will contain all relevant information, such as product names and line
                  items.
                </li>
                <li>Invoices will be denominated in USD.</li>
                <li>PayPal <strong>WILL</strong> reveal your personal information to the client, and vice versa in most
                  cases. Use Shield instead to avoid this.
                </li>
              </ul>
            </v-col>
            <v-col cols="12" class="text-center">
              <v-btn color="primary" variant="flat" @click="paypalWarned = true">I understand and wish to continue</v-btn>
            </v-col>
          </v-row>
          <v-row v-else-if="!paypal.ready">
            <v-col cols="12">
              <p>Enter your PayPal API Credentials below. <strong>These are not your username and password.</strong> You
                can get these credentials by following these steps:</p>
              <ol>
                <li>Log into your PayPal Dashboard.</li>
                <li>Click the 'Developer' link in the toolbar.</li>
                <li>Switch the toggle to 'Live' mode.</li>
                <li>Under 'REST API Apps', click the 'Create App' button. You can name the app anything,
                  but you might want to name it something like 'Artconomy Integration' so you remember what it is.
                </li>
                <li><strong>Optional, but highly recommended for security:</strong> Uncheck all of the features on the
                  app aside from 'Invoicing.'
                </li>
                <li>Copy your Client ID and Secret using the icons next to them, and paste them into the fields below,
                  and submit!
                </li>
              </ol>
              <v-alert type="info" class="mt-4">
                <strong>This feature is in beta. Please contact support if you encounter any issues!</strong>
              </v-alert>
            </v-col>
            <v-col cols="12" md="6" lg="4" offset-lg="2">
              <ac-bound-field
                  label="Client ID"
                  :field="paypalForm.fields.key"
                  hint="Your API Client ID."
                  :persistent-hint="true"
              />
            </v-col>
            <v-col cols="12" md="6" lg="4">
              <ac-bound-field
                  label="Secret"
                  :field="paypalForm.fields.secret"
                  type="password"
                  hint="Your API Secret."
                  :persistent-hint="true"
              />
            </v-col>
          </v-row>
          <ac-load-section :controller="paypalTemplates" v-else-if="paypal.ready">
            <template v-slot:default>
              <v-row>
                <v-col cols="12">
                  <ac-patch-field
                      :patcher="paypal.patchers.template_id"
                      :items="templateList"
                      label="PayPal Invoice Template"
                      hint="Select the PayPal invoice template Artconomy will fill with commission details.
                          Using an invoice template allows you to add line items like taxes or other business
                          address information on your invoices."
                      field-type="v-select"
                      item-text="name"
                      item-value="id"
                      :persistent-hint="true"
                  />
                </v-col>
                <v-col cols="12" md="6" class="text-md-center">
                  <ac-confirmation :action="deletePaypal">
                    <template v-slot:default="{on}">
                      <v-btn color="danger" variant="flat" class="cancel-subscription" v-on="on">Remove PayPal Integration</v-btn>
                    </template>
                    <template v-slot:confirmation-text>
                      <div>
                        <p>Are you sure you wish to disconnect PayPal?</p>
                      </div>
                    </template>
                  </ac-confirmation>
                </v-col>
                <v-col cols="12" md="6" class="text-md-center">
                  <v-alert type="success" v-if="paypal.x!.active">Your PayPal Integration is ready.</v-alert>
                  <v-alert type="warning" v-else>
                    You must select a valid template. A template must use USD to be valid.
                    <a href="https://www.paypal.com/invoice/s/settings/templates">You can configure your templates
                      here.</a>
                  </v-alert>
                </v-col>
              </v-row>
            </template>
          </ac-load-section>
        </v-card-text>
      </ac-form-dialog>
      <v-row no-gutters v-if="(subject!.landscape)">
        <v-col class="text-center" cols="12">
          <p>Your landscape subscription is paid through {{formatDate(userSubject.landscape_paid_through || '')}}.</p>
        </v-col>
        <v-col class="text-center" cols="12" sm="6" variant="flat">
          <v-btn :to="{name: 'Payment', params: {username}}" color="primary">Update Payment Settings</v-btn>
        </v-col>
        <v-col class="text-center" cols="12" sm="6" v-if="userSubject.landscape_enabled">
          <ac-confirmation :action="cancelSubscription">
            <template v-slot:default="{on}">
              <v-btn color="danger" class="cancel-subscription" v-on="on" variant="flat">Cancel Subscription</v-btn>
            </template>
            <template v-slot:confirmation-text>
              <div>
                <p>Are you sure you wish to cancel your subscription?</p>
                <p>Note: You will be able to use the extra features until your current term ends.</p>
              </div>
            </template>
          </ac-confirmation>
        </v-col>
        <v-col class="text-center" cols="12" sm="6" v-else-if="subject!.landscape">
          <v-btn color="secondary" :to="{name: 'Upgrade'}" variant="flat">Restart Subscription</v-btn>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import {useSubject} from '@/mixins/subjective.ts'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import {artCall} from '@/lib/lib.ts'
import {siDiscord} from 'simple-icons'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import {PaypalConfig} from '@/types/PaypalConfig.ts'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import {computed, ref, watch} from 'vue'
import {useForm} from '@/store/forms/hooks.ts'
import {useList} from '@/store/lists/hooks.ts'
import {useSingle} from '@/store/singles/hooks.ts'
import {statusOk} from '@/mixins/ErrorHandling.ts'
import SubjectiveProps from '@/types/SubjectiveProps.ts'
import {formatDate} from '@/lib/otherFormatters.ts'
import {User} from '@/store/profiles/types/User.ts'

const showPaypal = ref(false)
const paypalWarned = ref(false)

const props = defineProps<SubjectiveProps>()

const {subject, subjectHandler, subjectPlan} = useSubject({ props })

const userSubject = computed(() => subject.value as User)

const paypal = useSingle<PaypalConfig>(
    `paypal__${props.username}`,
    {endpoint: `/api/sales/account/${props.username}/paypal/`},
)

paypal.get().catch(statusOk(404))

const paypalTemplates = useList<{ name: string, id: string }>(
    `paypalTemplates__${props.username}`,
    {
      endpoint: `/api/sales/account/${props.username}/paypal/templates/`,
      paginated: false,
    },
)

const paypalForm = useForm(`paypalForm__${props.username}`, {
  endpoint: `/api/sales/account/${props.username}/paypal/`,
  fields: {
    key: {
      value: '',
      validators: [{name: 'required'}],
    },
    secret: {
      value: '',
      validators: [{name: 'required'}],
    },
  },
})

const adminPath = computed(() => {
  if (!subject.value) {
    return ''
  }
  return `${location.protocol}//${location.host}/admin/profiles/user/${subject.value.id}/`
})

const templateList = computed(() => {
  if (!paypalTemplates.ready) {
    return []
  }
  return paypalTemplates.list.map((item) => item.x!)
})

const deletePaypal = async () => {
  return paypal.delete().catch(paypalForm.setErrors)
}

const cancelSubscription = async () => {
  return artCall({
    url: `/api/sales/account/${props.username}/cancel-premium/`,
    method: 'post',
  }).then(
      subjectHandler.user.setX,
  )
}

watch(() => paypal.x, (paypal: PaypalConfig|null) => {
  if (!paypal) {
    return
  }
  paypalTemplates.firstRun()
})

defineExpose({subject})
</script>
