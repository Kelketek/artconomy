<template>
  <v-container>
    <ac-form-container :sending="claimForm.sending" :errors="claimForm.errors">
      <v-row no-gutters>
        <v-col class="text-center" cols="12">
          <h1>Your Order is waiting!</h1>
        </v-col>
        <v-col class="text-center" cols="12">
          <v-img :src="cheering" max-height="30vh" :contain="true"></v-img>
        </v-col>
        <v-col class="text-center" cols="12" v-if="isRegistered">
          <p>You are currently logged in as <strong>{{viewerName}}</strong>. Would you like to claim this order as
            {{viewerName}} or continue as a guest?</p>
        </v-col>
        <v-col class="text-center text-sm-right" cols="12" sm="6" v-if="isRegistered">
          <v-btn color="green" @click="claimAsUser" variant="flat">Claim as {{viewerName}}!</v-btn>
        </v-col>
        <v-col class="text-center text-sm-left" cols="12" sm="6" v-if="isRegistered">
          <v-btn @click="becomeGuest" variant="flat">Continue as guest</v-btn>
        </v-col>
        <v-col cols="12" v-for="field of claimForm.fields" :key="field.fieldName">
          <v-alert v-for="(error, index) of field.errors" :key="index" :value="true">
            {{error}}
          </v-alert>
        </v-col>
      </v-row>
    </ac-form-container>
  </v-container>
</template>

<script setup lang="ts">
import {useViewer} from '@/mixins/viewer.ts'
import {RouteLocationRaw, useRouter} from 'vue-router'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import {BASE_URL} from '@/lib/lib.ts'
import {useSocket} from '@/plugins/socket.ts'
import {useForm} from '@/store/forms/hooks.ts'
import {User} from '@/store/profiles/types/main'

const cheering = new URL('static/images/cheering.png', BASE_URL).href
const props = defineProps<{username?: string, orderId?: string, token?: string, deliverableId?: string, next?: string}>()
const router = useRouter()
const {rawViewerName, viewerName, viewerHandler, isRegistered} = useViewer()
const socket = useSocket()

const claimForm = useForm('orderClaim', {
  endpoint: '/api/sales/order-auth/',
  reset: false,
  fields: {
    id: {value: props.orderId},
    claim_token: {value: props.token},
    chown: {value: false},
  },
})

const visitOrder = (user: User) => {
  socket.socket?.reconnect()
  const route: RouteLocationRaw = {}
  if (props.next) {
    Object.assign(route, JSON.parse(props.next) as RouteLocationRaw)
    if (route.query === undefined) {
      route.query = {}
    }
  } else {
    Object.assign(route, {
      name: 'Order',
      params: {
        orderId: props.orderId,
        username: rawViewerName.value,
      },
    })
    if (props.deliverableId) {
      Object.assign(route, {
        name: 'OrderDeliverableOverview',
        params: {
          orderId: props.orderId,
          deliverableId: props.deliverableId,
          username: rawViewerName.value,
        },
      })
    }
  }
  const commentId = route.query?.commentId
  if (commentId) {
    route.query!.commentId = commentId
  }
  viewerHandler.user.setX(user)
  if (user.guest) {
    viewerHandler.artistProfile.kill()
    viewerHandler.artistProfile.setX(null)
    viewerHandler.artistProfile.ready = false
    viewerHandler.artistProfile.fetching = false
  }
  router.replace(route)
}

const sendForm = () => {
  if (!isRegistered.value) {
    claimForm.submitThen(visitOrder)
  }
}
if (socket.socket?.readyState) {
  sendForm()
} else {
  socket.connectListeners.ClaimOrder = sendForm
}

const claimAsUser = () => {
  claimForm.fields.chown.update(true)
  claimForm.submitThen(visitOrder)
}

const becomeGuest = () => {
  claimForm.fields.chown.update(false)
  claimForm.submitThen(visitOrder)
}
</script>
