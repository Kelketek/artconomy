<template>
  <v-list
    v-if="subject"
    v-model:opened="open"
    no-action
    nav
    density="compact"
    :role="nested ? undefined : 'list'"
  >
    <v-list-item
      :to="{ name: 'Options', params: { username } }"
      exact
      role="listitem"
      tabindex="0"
    >
      <v-list-item-title>Options</v-list-item-title>
      <template #append>
        <v-icon :icon="mdiWrench" />
      </template>
    </v-list-item>
    <v-list-item
      v-if="subject.artist_mode"
      class="artist-panel-link"
      :to="{ name: 'Artist', params: { username } }"
      exact
      role="listitem"
      tabindex="0"
    >
      <v-list-item-title>Artist</v-list-item-title>
      <template #append>
        <v-icon :icon="mdiPalette" />
      </template>
    </v-list-item>
    <v-list-item
      :to="{ name: 'Email', params: { username } }"
      exact
      role="listitem"
      tabindex="0"
    >
      <v-list-item-title>Email Notifications</v-list-item-title>
      <template #append>
        <v-icon :icon="mdiSend" />
      </template>
    </v-list-item>
    <v-list-item
      :to="{ name: 'Login Details', params: { username } }"
      role="listitem"
      tabindex="0"
    >
      <v-list-item-title>Login Details</v-list-item-title>
      <template #append>
        <v-icon :icon="mdiLock" />
      </template>
    </v-list-item>
    <v-list-item
      :to="{ name: 'Avatar', params: { username } }"
      role="listitem"
      tabindex="0"
    >
      <v-list-item-title>Avatar</v-list-item-title>
      <template #append>
        <v-icon :icon="mdiAccount" />
      </template>
    </v-list-item>
    <v-list-item
      v-if="isArtist"
      :to="{ name: 'Social', params: { username } }"
      role="listitem"
      tabindex="0"
    >
      <v-list-item-title>Social</v-list-item-title>
      <template #append>
        <v-icon :icon="mdiShare" />
      </template>
    </v-list-item>
    <v-list-item
      :to="{ name: 'Premium', params: { username } }"
      role="listitem"
      tabindex="0"
    >
      <v-list-item-title>Premium</v-list-item-title>
      <template #append>
        <v-icon :icon="mdiStar" />
      </template>
    </v-list-item>
    <v-list-group value="Payment" density="compact">
      <template #activator="activator">
        <v-list-item v-bind="activator.props" tabindex="0">
          <v-list-item-title>Payment</v-list-item-title>
        </v-list-item>
      </template>
      <v-list-item
        :to="{ name: 'Purchase', params: { username } }"
        role="listitem"
        tabindex="0"
      >
        <template #append>
          <v-icon :icon="mdiCreditCard" />
        </template>
        <v-list-item-title>Payment Methods</v-list-item-title>
      </v-list-item>
      <v-list-item
        v-if="showPayout"
        :to="{ name: 'Payout', params: { username } }"
        class="payout-link"
        role="listitem"
        tabindex="0"
      >
        <template #append>
          <v-icon :icon="mdiWallet" />
        </template>
        <v-list-item-title>Payout Methods</v-list-item-title>
      </v-list-item>
      <v-list-item
        :to="{ name: 'Invoices', params: { username } }"
        role="listitem"
        tabindex="0"
      >
        <template #append>
          <v-icon :icon="mdiReceiptText" />
        </template>
        <v-list-item-title>Invoices</v-list-item-title>
      </v-list-item>
      <v-list-item
        :to="{ name: 'TransactionHistory', params: { username } }"
        role="listitem"
        tabindex="0"
      >
        <template #append>
          <v-icon :icon="mdiListBox" />
        </template>
        <v-list-item-title>Raw Transaction History</v-list-item-title>
      </v-list-item>
    </v-list-group>
  </v-list>
</template>

<script setup lang="ts">
import { useSubject } from "@/mixins/subjective.ts"
import { computed, ref } from "vue"
import {
  mdiAccount,
  mdiCreditCard,
  mdiListBox,
  mdiLock,
  mdiPalette,
  mdiReceiptText,
  mdiSend,
  mdiShare,
  mdiStar,
  mdiWallet,
  mdiWrench,
} from "@mdi/js"
import { User } from "@sentry/vue"
import type { SubjectiveProps } from "@/types/main"
import { BankStatus } from "@/store/profiles/types/enums.ts"

const props = withDefaults(
  defineProps<SubjectiveProps & { nested?: boolean }>(),
  { nested: false },
)
const open = ref(["Payment"])
const { subjectHandler, subject } = useSubject({ props })
const inSupportedCountry = computed(() => {
  const profile = subjectHandler.artistProfile
  return (
    profile.x &&
    profile.x.bank_account_status === BankStatus.IN_SUPPORTED_COUNTRY
  )
})
const isArtist = computed(() => {
  return (subject.value as User).artist_mode
})
const showPayout = computed(() => {
  return (subject.value as User).artist_mode || inSupportedCountry.value
})
subjectHandler.artistProfile.get().then()
</script>
