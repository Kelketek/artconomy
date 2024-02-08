<template>
  <v-col>
    <ac-related-manager ref="manager" :list-controller="demoList" :field-controller="userForm.fields.user_id"
                        item-key="user">
      <template v-slot:preview="{item}">
        <v-col cols="4" sm="3" md="2" lg="1">
          <ac-avatar :user="item.x.user"
                     removable="true" @remove="item.delete().catch(userForm.setErrors)"/>
        </v-col>
      </template>
      <template v-slot:default="{filter}">
        <ac-bound-field
            :field="userForm.fields.user_id" field-type="ac-user-select" :multiple="false" :filter="filter"/>
      </template>
    </ac-related-manager>
  </v-col>
</template>

<script lang="ts">
import {Component, toNative} from 'vue-facing-decorator'
import AcRelatedManager from '../AcRelatedManager.vue'
import {FormController} from '@/store/forms/form-controller.ts'
import {ListController} from '@/store/lists/controller.ts'
import {User} from '@/store/profiles/types/User.ts'
import AcAvatar from '@/components/AcAvatar.vue'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import {ArtVue} from '@/lib/lib.ts'

@Component({
  components: {
    AcBoundField,
    AcAvatar,
    AcRelatedManager,
  },
})
class DummyRelated extends ArtVue {
  public demoList: ListController<User> = null as unknown as ListController<User>
  public userForm: FormController = null as unknown as FormController

  public created() {
    this.demoList = this.$getList('demoList', {
      endpoint: '/endpoint/',
      paginated: false,
    })
    this.userForm = this.$getForm('userForm', {
      endpoint: '/endpoint/',
      fields: {user_id: {value: null}},
    })
    this.demoList.get().then()
  }
}

export default toNative(DummyRelated)
</script>
