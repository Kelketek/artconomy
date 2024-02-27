<template>
  <v-row dense v-if="reference">
    <v-col cols="12">
      <ac-unread-marker :read="reference.read">
        <div class="pop-out-container">
          <v-btn icon absolute left color="secondary" variant="flat" class="pop-out-button" @click="refTab">
            <v-icon icon="mdi-tab"/>
          </v-btn>
          <ac-link
              :to="{name: `${baseName}DeliverableReference`, params: {...$route.params, referenceId: reference.id}}">
            <ac-asset :asset="reference" thumb-name="thumbnail" alt="Reference image for order. Click to read comments."/>
          </ac-link>
        </div>
      </ac-unread-marker>
    </v-col>
  </v-row>
</template>

<style scoped>
.pop-out-container {
  position: relative;
}
.pop-out-button {
  position: absolute;
  top: 4px;
  left: 4px;
  z-index: 1;
}
</style>

<script lang="ts">
import {Component, Prop, toNative, Vue} from 'vue-facing-decorator'
import AcUnreadMarker from '@/components/AcUnreadMarker.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import AcAsset from '@/components/AcAsset.vue'
import Reference from '@/types/Reference.ts'

@Component({
  components: {
    AcAsset,
    AcLink,
    AcUnreadMarker,
  },
})
class AcReference extends Vue {
  @Prop({required: true})
  public reference!: Reference

  @Prop({required: true})
  public baseName!: string

  public refTab() {
    window.open(this.reference.file.full, '_blank')
  }
}

export default toNative(AcReference)
</script>
