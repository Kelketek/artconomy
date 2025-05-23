<!--suppress HtmlUnknownTarget -->
<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <div class="col-12 text-center">
          <img class="legal-logo" :src="logo" alt="Artconomy.com" />
        </div>
        <div class="col-12 text-center home-title">
          <h1>Refund Policy</h1>
        </div>
      </v-col>
      <v-col cols="12">
        <p><strong>Last updated: April 1, 2023</strong></p>
        <p>
          Artconomy endeavors to satisfy all of its customers of any issues they
          have with products purchased through our platform. However, due to the
          nature of services rendered, this is not always possible. This
          document lays out under what circumstances Artconomy will issue
          refunds for services and products rendered.
        </p>
        <h2>Refund Qualifications</h2>
        <h3>Commissioned, Digitally Delivered Art</h3>
        <p>
          Artconomy will issue a refund on art which its staff has determined to
          not meet the requirements of the
          <router-link :to="{ name: 'CommissionAgreement' }">
            Commission Agreement
          </router-link>
          on the part of the artist, if the commission is covered by Artconomy
          Shield
        </p>
        <p>
          Artists may also elect to refund a customer before scheduled delivery
          and without waiting for dispute resolution at their discretion.
        </p>
        <p>
          Refunds provided by Artconomy staff as part of Artconomy Shield will
          be minus the full escrow fees due to Artconomy.
        </p>
        <h3>Commissioned, Physically Delivered Art, or Physical Items</h3>
        <p>
          Artists must use shipping methods that provide tracking information
          and insurance which at least covers the cost of the item, and artists
          are authorized to add reasonable shipping costs to the price of any
          deliverable to meet this obligation.
        </p>
        <p>
          Risk of loss passes to the commissioner when an artist delivers goods
          to a common carrier. However, in the event of loss, the artist must
          make commercially reasonable efforts to collect on the insurance for
          the shipment for the benefit of the commissioner. Additionally, the
          artist must provide reasonable documentation of such efforts to the
          commissioner. If reasonable documentation is not provided, the
          commissioner may be refunded, minus Artconomy's Escrow fees, and any
          explicitly marked non-refundable costs agreed to upfront by the
          commissioner and artist.
        </p>
        <p>
          If the artist fails to obtain insurance for the shipment, risk of loss
          passes to the commissioner upon shipment to the destination specified
          by the commissioner.
        </p>
        <h3>Artconomy Subscription Services</h3>
        <p>
          Artconomy subscription services may be refunded if a refund is
          requested within three business days of purchase or renewal.
        </p>
        <p>
          If a subscription service changes its features or pricing relevant to
          your activity (such as fees on transactions) during your current
          billing cycle, or within three days of a billing cycle, you may cancel
          your subscription service and receive a refund for any monthly dues
          for that period. Any usage fees incurred during that period will
          either be removed or adjusted to their previous values for the cycle,
          at the discretion of Artconomy. For the purposes of this clause, a
          billing cycle will be considered monthly, even if the client has
          agreed to a longer cycle. Cancellation of service in these cases will
          result in prorated refunds for the remaining time.
        </p>
        <h2>Refund Fees</h2>
        <p>
          As Artconomy does not control the refund policy of artists on the
          platform, Artconomy will always be entitled to its fees for its escrow
          service, even when the artist performs the refund.
        </p>
        <p>
          No fees are required for refunding of Artconomy Subscription services.
        </p>
        <p>
          Artconomy does not collect fees from commissioners on commissions not
          covered by Artconomy Shield, but fees may be assessed according to the
          terms of any payment processor the commissioner and artist agree to
          use. Artconomy does not offer any refunds for non-shield commissions.
        </p>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { BASE_URL } from "@/lib/lib.ts"

const logo = new URL("/static/images/logo.svg", BASE_URL).href
</script>

<style scoped>
.legal-logo {
  width: 20%;
}
</style>
