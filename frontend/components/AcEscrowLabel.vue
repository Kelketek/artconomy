<template>
  <v-flex text-xs-center>
    <v-flex xs12 v-if="escrow">
      <v-icon large class="green--text">fa-shield</v-icon>
    </v-flex>
    <v-flex xs12 v-else>
      <v-icon large class="yellow--text">warning</v-icon>
    </v-flex>
    <v-flex xs12 text-xs-center v-if="escrow">
      <p>
        This {{name}} protected by <br />
        <router-link :to="{name: 'BuyAndSell', params: {question: 'shield'}}">
          Artconomy Shield.
        </router-link>
      </p>
    </v-flex>
    <v-flex xs12 text-xs-center v-else>
      <p>
        This {{name}} is not protected by <br />
        <router-link :to="{name: 'BuyAndSell', params: {question: 'shield'}}">
          Artconomy Shield.
        </router-link>
      </p>
    </v-flex>
  </v-flex>
</template>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import {Prop} from 'vue-property-decorator'

@Component
export default class AcEscrowLabel extends Vue {
  @Prop({required: true})
  public escrow!: boolean
  @Prop({required: true})
  public name!: string
}
</script>
