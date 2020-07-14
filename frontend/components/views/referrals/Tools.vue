<template>
  <v-container>
    <v-row no-gutters  >
      <v-col class="text-center" cols="12" >
        <h1>Referral Tools</h1>
      </v-col>
      <v-col class="text-center" cols="12" lg="6" >
        <v-card>
          <v-card-text>
            <p>You can embed a copy of your store into your website by using the following code snippet:</p>
            <code>
              &lt;iframe src="{{protocol}}//{{host}}/store/{{username}}/iframe/?referred_by={{username}}"
              width="100%" height="500"&gt;&lt;/iframe&gt;
            </code>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col class="text-center" cols="12" lg="6" >
        <v-card>
          <v-card-text>
            <p>
              <strong>Show your commission status at a glance!</strong>
            </p>
            <code>
              &lt;a href="{{protocol}}//{{host}}/store/{{username}}/iframe/?referred_by={{username}}"&gt;&lt;img
              src="{{protocol}}//{{host}}/api/sales/v1/account/{{username}}/commissions-status-image/"&gt;&lt;/a&gt;
            </code>
            <p>Preview:</p>
            <router-link :to="{name: 'Store', params: {username: username}}">
              <img :src="`/api/sales/v1/account/${username}/commissions-status-image/`">
            </router-link>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Subjective from '@/mixins/subjective'

  @Component
export default class Tools extends mixins(Subjective) {
  public get host() {
    return window.location.hostname
  }

  public get protocol() {
    return window.location.protocol
  }
}
</script>
