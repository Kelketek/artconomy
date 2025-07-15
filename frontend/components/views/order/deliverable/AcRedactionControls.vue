<template>
  <v-card v-if="showRedactionOptions" class="my-2">
    <v-card-text>
      <v-row>
        <v-col v-if="redactedOn" cols="12" class="text-center">
          <v-alert type="info"
            >This deliverable was redacted on
            {{ formatDate(redactedOn) }}</v-alert
          >
        </v-col>
        <v-col v-else cols="12" class="text-center">
          <p v-if="redactAvailableOn && !redactDatePassed">
            <router-link
              :to="{
                name: 'BuyAndSell',
                params: { question: 'what-is-redaction' },
              }"
              >Redaction</router-link
            >
            will be available on {{ formatDate(redactAvailableOn) }}.
          </p>
          <p v-if="redactAvailable">
            You may
            <router-link
              :to="{
                name: 'BuyAndSell',
                params: { question: 'what-is-redaction' },
              }"
              >redact</router-link
            >
            this deliverable to clear most details.
            <ac-confirmation :action="performRedaction">
              <template #default="{ on }">
                <v-btn v-on="on">Redact</v-btn>
              </template>
              <template #confirmation-text>
                This will remove most details from the order, including your
                revisions and the references given. This cannot be undone!
              </template>
            </ac-confirmation>
          </p>
          <p v-if="autoRedactOn">
            This deliverable will automatically be redacted on
            {{ formatDate(autoRedactOn) }}
          </p>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from "vue"
import {
  DeliverableProps,
  useDeliverable,
} from "@/components/views/order/mixins/DeliverableMixin.ts"
import { DeliverableStatus as S } from "@/types/enums/DeliverableStatus.ts"
import { parseISO, formatDate } from "@/lib/otherFormatters.ts"
import AcConfirmation from "@/components/wrappers/AcConfirmation.vue"

const props = defineProps<DeliverableProps>()

const {
  deliverable,
  characters,
  references,
  revisions,
  isSeller,
  isArbitrator,
  is,
  statusEndpoint,
} = useDeliverable(props)

const refetchData = () => {
  characters.get()
  references.get()
  revisions.get()
}

const staffRedactableStatus = computed(() =>
  is(
    S.COMPLETED,
    S.REFUNDED,
    S.NEW,
    S.PAYMENT_PENDING,
    S.LIMBO,
    S.MISSED,
    S.CANCELLED,
    S.WAITING,
  ),
)

const sellerRedactableStatus = computed(() =>
  is(S.COMPLETED, S.REFUNDED, S.CANCELLED),
)

const redactAvailableOn = computed(() => {
  if (!deliverable.x) {
    return null
  }
  if (!deliverable.x.redact_available_on) {
    return null
  }
  return parseISO(deliverable.x.redact_available_on)
})

const redactDatePassed = computed(() => {
  if (!redactAvailableOn.value) {
    return false
  }
  return redactAvailableOn.value < new Date()
})

const redactAvailable = computed(() => {
  if (isArbitrator.value) {
    return true
  }
  return redactDatePassed.value
})

const showRedactionOptions = computed(() => {
  if (!deliverable.x) {
    return false
  }
  if (!(isSeller.value || isArbitrator.value)) {
    return false
  }
  if (isArbitrator.value && staffRedactableStatus.value) {
    return true
  }
  return isSeller.value && sellerRedactableStatus.value
})

const redactedOn = computed(() => {
  if (!deliverable.x) {
    return null
  }
  if (!deliverable.x.redacted_on) {
    return null
  }
  return parseISO(deliverable.x.redacted_on)
})

const autoRedactOn = computed(() => {
  if (!deliverable.x) {
    return null
  }
  if (!deliverable.x.auto_redact_on) {
    return null
  }
  return parseISO(deliverable.x.auto_redact_on)
})

const performRedaction = async () => {
  statusEndpoint("redact")().then(() => {
    if (deliverable.x!.redacted_on) {
      refetchData()
    }
  })
}
</script>
