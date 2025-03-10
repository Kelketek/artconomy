<template>
  <v-row dense>
    <v-col
      v-if="escrow"
      cols="12"
      class="text-center"
    >
      <v-icon
        size="large"
        color="green"
        :icon="mdiShieldHalfFull"
      />
    </v-col>
    <v-col
      v-else-if="!upgradeAvailable"
      cols="12"
      class="text-center"
    >
      <v-icon
        size="large"
        color="yellow"
        :icon="mdiAlert"
      />
    </v-col>
    <v-col
      v-else
      cols="12"
      class="text-center"
    >
      <v-icon
        size="large"
        :icon="mdiShieldHalfFull"
      />
    </v-col>
    <v-col
      v-if="escrow"
      class="text-center"
      cols="12"
    >
      <p>
        This {{ name }} protected by <br>
        <router-link :to="{name: 'BuyAndSell', params: {question: 'shield'}}">
          Artconomy Shield.
        </router-link>
      </p>
    </v-col>
    <v-col
      v-else-if="!upgradeAvailable"
      class="text-center"
      cols="12"
    >
      <p>
        This {{ name }} is not protected by <br>
        <router-link :to="{name: 'BuyAndSell', params: {question: 'shield'}}">
          Artconomy Shield.
        </router-link>
      </p>
    </v-col>
    <v-col
      v-else
      class="text-center"
    >
      This product offers Artconomy Shield protection as an upgrade.
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import {mdiAlert, mdiShieldHalfFull} from '@mdi/js'

withDefaults(
  defineProps<{escrow: boolean, upgradeAvailable?: boolean, name: string}>(),
  {upgradeAvailable: false},
)
</script>
