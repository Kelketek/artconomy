<template>
  <ac-load-section :controller="notificationSettings">
    <template #default>
      <v-card>
        <v-card-text>
          <v-list-subheader class="pt-5 mt-5">
            <strong>Community</strong>
          </v-list-subheader>
          <v-divider />
          <v-row>
            <v-col
              cols="12"
              sm="6"
              md="4"
            >
              <ac-patch-field
                field-type="v-switch"
                label="Direct Messages"
                hint="Send you an email when you receive a new direct message"
                :persistent-hint="true"
                color="primary"
                :patcher="notificationSettings.patchers.new_comment__conversation"
              />
            </v-col>
            <v-col
              cols="12"
              sm="6"
              md="4"
            >
              <ac-patch-field
                field-type="v-switch"
                label="Commissions Open"
                hint="Send you an email when an artist you are watching opens their commissions"
                :persistent-hint="true"
                color="primary"
                :patcher="notificationSettings.patchers.commission_slots_available"
              />
            </v-col>
            <v-col
              cols="12"
              sm="6"
              md="4"
            >
              <ac-patch-field
                field-type="v-switch"
                label="Referral Credit"
                hint="Email you when someone you've referred qualifies you for a free month of Landscape"
                :persistent-hint="true"
                color="primary"
                :patcher="notificationSettings.patchers.referral_landscape_credit"
              />
            </v-col>
          </v-row>
          <v-list-subheader class="pt-5 mt-5">
            <strong>Order/Sale Updates</strong>
          </v-list-subheader>
          <v-divider />
          <v-row>
            <v-col cols="12">
              <v-alert type="warning">
                You are strongly advised to keep these notifications enabled, as missing them could cause you to
                lose in dispute resolution or on responses from your commissioner/artist.
              </v-alert>
            </v-col>
            <v-col
              cols="12"
              sm="6"
              md="4"
            >
              <ac-patch-field
                field-type="v-switch"
                :patcher="notificationSettings.patchers.order_update"
                label="Order/Sale activity updates"
                :persistent-hint="true"
                color="primary"
                hint="Notifications on order/sale status updates, newly uploaded references and revisions/WIPs"
              />
            </v-col>
            <v-col
              cols="12"
              sm="6"
              md="4"
            >
              <ac-patch-field
                field-type="v-switch"
                :patcher="notificationSettings.patchers.new_comment__deliverable"
                label="Comments on Orders/Sales"
                :persistent-hint="true"
                color="primary"
                hint="Comments on orders/sales, or their respective referenes and revisions/WIPs"
              />
            </v-col>
            <v-col
              cols="12"
              sm="6"
              md="4"
            >
              <ac-patch-field
                field-type="v-switch"
                :patcher="notificationSettings.patchers.wait_list_updated"
                label="Waitlist updated"
                color="primary"
                hint="Notify you when an order has been placed on a waitlisted product"
                :persistent-hint="true"
              />
            </v-col>
          </v-row>
          <v-list-subheader class="pt-5 mt-5">
            <strong>
              Account Issues
            </strong>
          </v-list-subheader>
          <v-divider />
          <v-row class="pb-4">
            <v-col
              cols="12"
              sm="6"
              md="4"
            >
              <ac-patch-field
                field-type="v-switch"
                :patcher="notificationSettings.patchers.renewal_failure"
                label="Subscription Renewal Issues"
                :persistent-hint="true"
                color="primary"
                hint="Inform you if we're having trouble billing you for your subcription services"
              />
            </v-col>
            <v-col
              cols="12"
              sm="6"
              md="4"
            >
              <ac-patch-field
                field-type="v-switch"
                :patcher="notificationSettings.patchers.commissions_automatically_closed"
                label="Commissions Automatically Closed"
                :persistent-hint="true"
                color="primary"
                hint="Inform you if Artconomy has automatically closed your commissions,
                  which may happen if orders are ignored"
              />
            </v-col>
            <v-col
              cols="12"
              sm="6"
              md="4"
            >
              <ac-patch-field
                field-type="v-switch"
                :patcher="notificationSettings.patchers.bank_transfer_failed"
                label="Bank Transfer Failed"
                :persistent-hint="true"
                color="primary"
                hint="Give you a heads up if we're having trouble sending you money and need you to take a look at it"
              />
            </v-col>
          </v-row>
          <v-list-subheader class="pt-5 mt-5">
            <strong>
              Required Notifications
            </strong>
          </v-list-subheader>
          <v-divider />
          <v-row>
            <v-col cols="12">
              <v-alert type="info">
                These notifications are required, either for legal or technical reasons. The only way to stop receiving
                these notifications is to delete your account,
                <router-link :to="{name: 'Login Details', params: {username}}">
                  which you can do here
                </router-link>
                .
              </v-alert>
            </v-col>
          </v-row>
          <v-row>
            <v-col
              cols="12"
              sm="6"
              md="4"
            >
              <v-switch
                label="Policy Updates"
                :disabled="true"
                :model-value="true"
                color="primary"
                :persistent-hint="true"
                hint="Information about policy and terms of service updates which may affect you"
              />
            </v-col>
            <v-col
              cols="12"
              sm="6"
              md="4"
            >
              <v-switch
                label="Direct Contact for Account Issues"
                :disabled="true"
                :model-value="true"
                :persistent-hint="true"
                color="primary"
                hint="Staffers may contact you directly if we detect an issue with your account"
              />
            </v-col>
            <v-col
              cols="12"
              sm="6"
              md="4"
            >
              <v-switch
                label="Terms of Service Violations"
                :disabled="true"
                :model-value="true"
                :persistent-hint="true"
                color="primary"
                hint="We may notify you if we have to take action on your account or content due to terms of service violations."
              />
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </template>
  </ac-load-section>
</template>

<script setup lang="ts">
import AcPatchField from '@/components/fields/AcPatchField.vue'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import {useSingle} from '@/store/singles/hooks.ts'
import type {NotificationSettings, SubjectiveProps} from '@/types/main'

const props = defineProps<SubjectiveProps>()

const notificationSettings = useSingle<NotificationSettings>(
    `${props.username}__notificationPrefs`,
    {endpoint: `/api/profiles/account/${props.username}/notification-settings/`},
)

notificationSettings.get().then()
</script>
