<template>
  <v-row no-gutters>
    <ac-related-manager
        :field-controller="newShare.fields.user_id" :list-controller="controller"
        item-key="user"
    >
      <template v-slot:preview="{item}">
        <v-col cols="4" sm="3" md="2" lg="1">
          <ac-avatar :user="item.x!.user" :removable="true" @remove="item.delete().catch(newShare.setErrors)"/>
        </v-col>
      </template>
      <template v-slot:default="{filter}">
        <v-col cols="12">
          <ac-bound-field
              label="Share with..."
              hint="Enter the username of another Artconomy user to share this with them."
              :field="newShare.fields.user_id" field-type="ac-user-select" :multiple="false" :filter="filter"/>
        </v-col>
      </template>
    </ac-related-manager>
  </v-row>
</template>

<script lang="ts">
import AcAvatar from './AcAvatar.vue'
import AcRelatedManager from './wrappers/AcRelatedManager.vue'
import AcLoadSection from './wrappers/AcLoadSection.vue'
import AcBoundField from './fields/AcBoundField'
import {Component, Prop, toNative} from 'vue-facing-decorator'
import {ArtVue, genId} from '@/lib/lib'
import {FormController} from '@/store/forms/form-controller'
import {ListController} from '@/store/lists/controller'
import {TerseUser} from '@/store/profiles/types/TerseUser'

@Component({
  components: {
    AcBoundField,
    AcLoadSection,
    AcRelatedManager,
    AcAvatar,
  },
})
class AcShareManager extends ArtVue {
  @Prop({required: true})
  public controller!: ListController<TerseUser>

  public newShare: FormController = null as unknown as FormController

  public created() {
    this.newShare = this.$getForm('share_' + genId(), {
      endpoint: this.controller.endpoint,
      fields: {user_id: {value: null}},
    })
  }
}

export default toNative(AcShareManager)
</script>

<style scoped>

</style>
