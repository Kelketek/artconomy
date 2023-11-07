<template>
  <v-row dense>
    <v-col cols="12" v-if="escrow" class="text-center">
      <v-icon size="large" color="green" icon="mdi-shield-half-full"/>
    </v-col>
    <v-col cols="12" v-else-if="!upgradeAvailable" class="text-center">
      <v-icon size="large" color="yellow" icon="mdi-alert"/>
    </v-col>
    <v-col cols="12" v-else class="text-center">
      <v-icon size="large" icon="mdi-shield-half-full"/>
    </v-col>
    <v-col class="text-center" cols="12" v-if="escrow">
      <p>
        This {{name}} protected by <br/>
        <router-link :to="{name: 'BuyAndSell', params: {question: 'shield'}}">
          Artconomy Shield.
        </router-link>
      </p>
    </v-col>
    <v-col class="text-center" cols="12" v-else-if="!upgradeAvailable">
      <p>
        This {{name}} is not protected by <br/>
        <router-link :to="{name: 'BuyAndSell', params: {question: 'shield'}}">
          Artconomy Shield.
        </router-link>
      </p>
    </v-col>
    <v-col class="text-center" v-else>
      This product offers Artconomy Shield protection as an upgrade.
    </v-col>
  </v-row>
</template>

<script lang="ts">
import {Component, Prop, toNative, Vue} from 'vue-facing-decorator'

@Component
class AcEscrowLabel extends Vue {
  @Prop({required: true})
  public escrow!: boolean

  @Prop({default: false})
  public upgradeAvailable!: boolean

  @Prop({required: true})
  public name!: string
}

export default toNative(AcEscrowLabel)
</script>
