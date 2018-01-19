<template>
  <div class="container">
    <div class="row">
      <div class="col-12">
        <div class="col-12 text-center">
          <img class="legal-logo" src="/static/images/logo.svg"/>
        </div>
        <div class="col-12 text-center home-title">
          <h1>Refund Policy</h1>
        </div>
      </div>
      <div class="col-12-sm">
        <p>
          Artconomy endeavors to satisfy all of its customers of any issues they have with products purchased through our platform. However, due to the nature of services rendered, this is not always possible. This document lays out under what circumstances Artconomy will issue refunds for services and products rendered.
        </p>
        <h2>Refund Qualifications</h2>
        <h3>Commissioned, Digitally Delivered Art</h3>
        <p>
          Artconomy will issue a refund on art which has determined to not meet the requirements of the
          <router-link :to="{name: 'CommissionAgreement'}">Commission Agreement</router-link>
          on the part of the artist.
        </p>
        <p>
          Artists may also elect to refund a customer before scheduled delivery and without waiting
          for dispute resolution at their discretion.
        </p>
        <h3>Commissioned, Physically Delivered Art, or Physical Items</h3>
        <p>
          Artists are expected to use shipping methods which have tracking information and
          insurance which at least covers the cost of the item, and to use
          adjustments in the pricing to account for shipping requirements.
        </p>
        <p>
          In the case that an artist does not use a trackable shipping method and the deliverable does not arrive within
          a reasonable timeframe for the shipping service, the commissioner will receive a full refund.
        </p>
        <p>
          As physical items are unique pieces, items which are lost by the courier or which arrive broken will require the artist to file a dispute with the shipper.
          The artist will render the verdict from the courier on whether insurance can be collected. The artist will provide documentation from the courier on the insurance claim.
        </p>
        <p>
          If the courier's documentation shows that insurance will be remitted, the commissioner will be refunded, and the
          artist will be expected to recuperate costs from the courier.
        </p>
        <p>
          If the courier indicates that the artist has made an error (such as a wrong address specified, or not meeting
          packing requirements), they will be expected to attempt correction of the error. If the error is uncorrectable,
          the commissioner will be refunded.
        </p>
        <p>
          If the courier indicates that the package was delivered successfully and does not consider evidence of any
          damage provided to be covered under their insurance policy, no refund will be issued.
        </p>
        <h3>Artconomy Subscription Services</h3>
        <p>
          Artconomy subscription services may be refunded if a refund is requested within three business days of
          purchase or renewal.
        </p>
        <h2>Refund Fees</h2>
        <p>
          Artists are required to cover the cost of processing any refunds related to their sales.
        </p>
        <p>
          No fees are required for refunding of Artconomy Subscription services.
        </p>
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'commission-agreement'
  }
</script>

<style scoped>
   .legal-logo {
     width: 20%;
   }
</style>