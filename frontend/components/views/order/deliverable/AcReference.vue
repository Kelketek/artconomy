<template>
  <v-row dense>
    <v-col cols="12">
      <ac-unread-marker :read="reference.read">
        <div class="pop-out-container">
          <v-btn fab absolute left color="secondary" class="pop-out-button" @click="refTab">
            <v-icon>tab</v-icon>
          </v-btn>
          <ac-link :to="{name: `${baseName}DeliverableReference`, params: {...$route.params, referenceId: reference.id}}">
            <ac-asset :asset="reference" thumb-name="thumbnail" />
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
</style>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import AcUnreadMarker from '@/components/AcUnreadMarker.vue'
import {Prop} from 'vue-property-decorator'
import AcLink from '@/components/wrappers/AcLink.vue'
import AcAsset from '@/components/AcAsset.vue'
import Reference from '@/types/Reference'

@Component({
  components: {AcAsset, AcLink, AcUnreadMarker},
})
export default class AcReference extends Vue {
  @Prop({required: true})
  public reference!: Reference

  @Prop({required: true})
  public baseName!: string

  public refTab() {
    window.open(this.reference.file.full, '_blank')
  }
}
</script>
