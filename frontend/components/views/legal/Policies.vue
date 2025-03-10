<template>
  <v-container>
    <v-row>
      <v-col
        cols="12"
        md="3"
      >
        <v-card>
          <router-link :to="{name: 'CommissionAgreement'}">
            <v-card-title>Commission Agreement</v-card-title>
            <v-card-text>
              <h6 class="card-subtitle mb-2 text-muted">
                Click to Read
              </h6>
              <p class="card-text">
                Our commissioning agreement is the terms under which art is commissioned on Artconomy.
                Artists and commissioners should both be familiar with it. It contains information about what
                expectations are placed on both parties, and how Artconomy handles dispute resolution between both
                parties.
              </p>
            </v-card-text>
          </router-link>
        </v-card>
      </v-col>
      <v-col
        cols="12"
        md="3"
      >
        <v-card>
          <router-link :to="{name: 'RefundPolicy'}">
            <v-card-title>Refund Policy</v-card-title>
            <v-card-text class="card-block pt-2 pb-2">
              <h6 class="card-subtitle mb-2 text-muted">
                Click to Read
              </h6>
              <p class="card-text">
                Our refund policy contains details under which circumstances refunds may be remitted for services or
                products purchased on Artconomy.
              </p>
            </v-card-text>
          </router-link>
        </v-card>
      </v-col>
      <v-col
        cols="12"
        md="3"
      >
        <v-card>
          <router-link :to="{name: 'PrivacyPolicy'}">
            <v-card-title>Privacy Policy</v-card-title>
            <v-card-text>
              <p>Read how we use your data, and how we do not.</p>
            </v-card-text>
          </router-link>
        </v-card>
      </v-col>
      <v-col
        cols="12"
        md="3"
      >
        <v-card>
          <router-link :to="{name: 'TermsOfService'}">
            <v-card-title>Terms of Service</v-card-title>
            <v-card-text>
              <p>Read our site-wide terms of service.</p>
            </v-card-text>
          </router-link>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
</script>
