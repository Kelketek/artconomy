<template>
  <div class="container">
    <div class="row pb-2">
        <div class="card col-3">
          <router-link :to="{name: 'CommissionAgreement'}">
            <div class="card-block pt-2 pb-2">
              <h4 class="card-title">Commission Agreement</h4>
              <h6 class="card-subtitle mb-2 text-muted">Click to Read</h6>
              <p class="card-text">
                Our commissioning agreement is the terms under which art is commissioned on Artconomy.
                Artists and commissioners should both be familiar with it. It contains information about what
                expectations are placed on both parties, and how Artconomy handles dispute resolution between both
                parties.
              </p>
            </div>
          </router-link>
        </div>
      <div class="card col-3">
        <router-link :to="{name: 'RefundPolicy'}">
          <div class="card-block pt-2 pb-2">
            <h4 class="card-title">Refund Policy</h4>
            <h6 class="card-subtitle mb-2 text-muted">Click to Read</h6>
            <p class="card-text">
              Our refund policy contains details under which circumstances refunds may be remitted for services or
              products purchased on Artconomy.
            </p>
          </div>
        </router-link>
      </div>
      <div class="card col-3">
        <div class="card-block pt-2 pb-2">
          <h4 class="card-title">Privacy Policy</h4>
          <h6 class="card-subtitle mb-2 text-muted">To Be Written</h6>
          <p class="card-text">
            Read how we use your data, and how we do not.
          </p>
        </div>
      </div>
      <div class="card col-3">
        <div class="card-block pt-2 pb-2">
          <h4 class="card-title">Terms of Service</h4>
          <h6 class="card-subtitle mb-2 text-muted">To Be Written</h6>
          <p class="card-text">
            Read our site-wide terms of service.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'Policies'
  }
</script>